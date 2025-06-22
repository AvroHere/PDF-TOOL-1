#!/usr/bin/env python3
import fitz  # PyMuPDF
import hashlib
import os
import re
import zipfile
from datetime import datetime
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo

def display_manual():
    """Show user-friendly manual in terminal."""
    print("""
=== PDF Editor ===
Functions:
1. Remove duplicate images
   - Removes repeated images based on count/size thresholds
   - Saves cleaned PDF and ZIP of removed duplicates
2. Remove pages
   - Deletes specified pages (e.g., '1,3-5,7')
   - Saves modified PDF
3. Merge PDFs
   - Combines multiple PDFs in alphabetical order
   - Output: merged_final.pdf (saved in script's folder)
4. Split PDF
   - Extracts page ranges (e.g., '4', '7-13', '1-10,12-18')
   - Saves each range as separate PDF
5. Special Split
   - Extracts specific pages/ranges into one PDF (e.g., '1+4+11-16')
   - Creates single PDF with selected pages

""")

def get_pdf_path(multiple=False):
    """Get PDF path(s) with proper Tkinter cleanup."""
    root = Tk()
    root.withdraw()
    if multiple:
        paths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        root.destroy()
        return paths if paths else None
    else:
        path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        root.destroy()
        return path if path else None

def parse_page_range(page_str, total_pages):
    """Convert input like '1,3-5' into sorted list of page numbers (1-based)."""
    pages = set()
    for part in re.split(r'[,\s]+', page_str.strip()):
        if not part:
            continue
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= total_pages)

def parse_special_split(page_spec, total_pages):
    """Parse special split input like '1+4+11-16' into page numbers."""
    pages = set()
    for part in re.split(r'\+', page_spec.strip()):
        if not part:
            continue
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= total_pages)

def remove_pages(input_pdf, output_pdf, page_range):
    """Remove specified pages from PDF."""
    doc = fitz.open(input_pdf)
    total_pages = len(doc)
    
    if not page_range:
        print("No pages to remove!")
        doc.close()
        return False

    # Convert to 0-based and remove duplicates
    pages_to_remove = sorted({p-1 for p in page_range}, reverse=True)
    
    for page_num in pages_to_remove:
        doc.delete_page(page_num)
    
    doc.save(output_pdf)
    doc.close()
    return True

def get_image_hash(img_data):
    """Generate MD5 hash for image data."""
    return hashlib.md5(img_data).hexdigest()

def remove_duplicates(input_pdf, output_pdf, export_zip, repeat_threshold, min_size_kb):
    """Remove duplicate images from PDF."""
    doc = fitz.open(input_pdf)
    image_counts = {}
    removed_hashes = set()
    removed_images = []
    min_size_bytes = min_size_kb * 1024

    # First pass: Count image occurrences
    for page in doc:
        for img in page.get_images():
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_data = base_image["image"]
            img_ext = base_image["ext"]
            img_size = len(img_data)
            img_hash = get_image_hash(img_data)

            if img_hash in image_counts:
                image_counts[img_hash][0] += 1
                image_counts[img_hash][1].append((xref, img_data, img_ext, img_size))
            else:
                image_counts[img_hash] = [1, [(xref, img_data, img_ext, img_size)]]

    # Second pass: Remove duplicates
    duplicates_removed = 0
    for img_hash, (count, xrefs) in image_counts.items():
        if count >= repeat_threshold and len(xrefs[0][1]) >= min_size_bytes:
            for xref, img_data, img_ext, img_size in xrefs[1:]:  # Keep first occurrence
                for page in doc:
                    try:
                        page.delete_image(xref)
                        duplicates_removed += 1
                        if img_hash not in removed_hashes:
                            removed_images.append((img_data, img_ext, img_hash))
                            removed_hashes.add(img_hash)
                        break
                    except:
                        continue

    # Save outputs
    doc.save(output_pdf)
    doc.close()

    if duplicates_removed > 0:
        with zipfile.ZipFile(export_zip, 'w') as zipf:
            for img_data, ext, img_hash in removed_images:
                zipf.writestr(f"duplicate_{img_hash[:8]}.{ext}", img_data)

    return (sum(count for count, _ in image_counts.values()), 
            duplicates_removed, 
            len(removed_hashes))

def merge_pdfs(pdf_paths, output_path):
    """Merge multiple PDFs into one, sorted by filename."""
    merged_doc = fitz.open()
    
    for pdf_path in sorted(pdf_paths):
        try:
            doc = fitz.open(pdf_path)
            merged_doc.insert_pdf(doc)
            doc.close()
            print(f"Added: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"Error merging {pdf_path}: {e}")
            continue
    
    if len(merged_doc) > 0:
        merged_doc.save(output_path)
        merged_doc.close()
        return True
    else:
        merged_doc.close()
        return False

def split_pdf(input_pdf, page_ranges):
    """Split PDF into multiple files based on page ranges."""
    input_name = os.path.splitext(os.path.basename(input_pdf))[0]
    input_dir = os.path.dirname(input_pdf)
    doc = fitz.open(input_pdf)
    
    created_files = []
    for i, (start, end) in enumerate(page_ranges, 1):
        output_pdf = os.path.join(input_dir, f"{input_name}_pages_{start}-{end}.pdf")
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
        new_doc.save(output_pdf)
        new_doc.close()
        created_files.append(output_pdf)
        print(f"Created: {os.path.basename(output_pdf)}")
    
    doc.close()
    return created_files

def special_split_pdf(input_pdf, page_spec):
    """Create new PDF with specified pages/ranges."""
    doc = fitz.open(input_pdf)
    total_pages = len(doc)
    new_doc = fitz.open()
    
    pages_to_extract = parse_special_split(page_spec, total_pages)
    if not pages_to_extract:
        print("No valid pages specified!")
        return None
    
    for page_num in pages_to_extract:
        new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
    
    input_name = os.path.splitext(os.path.basename(input_pdf))[0]
    output_pdf = os.path.join(os.path.dirname(input_pdf), 
                            f"{input_name}_extracted.pdf")
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()
    
    return output_pdf

def main():
    display_manual()

    # Choose function first to determine if we need single or multiple files
    while True:
        choice = input("\nChoose function (1-5): ").strip()
        if choice in ('1', '2', '3', '4', '5'):
            break
        print("Invalid choice. Please enter 1-5.")

    start_time = datetime.now()
    success = False
    output_files = []

    if choice == '1':
        # Image deduplication
        input_pdf = get_pdf_path()
        if not input_pdf:
            print("No file selected. Exiting.")
            return
        
        input_dir = os.path.dirname(input_pdf)
        input_name = os.path.splitext(os.path.basename(input_pdf))[0]
        output_pdf = os.path.join(input_dir, f"{input_name}_clean.pdf")

        try:
            repeat_threshold = int(input("Minimum repeat count (default 5): ") or 5)
            min_size_kb = int(input("Minimum image size in KB (default 2): ") or 2)
            zip_name = input("ZIP name (default 'removed_images'): ") or "removed_images"
            export_zip = os.path.join(input_dir, f"{zip_name}.zip")

            total, removed, unique = remove_duplicates(
                input_pdf, output_pdf, export_zip, 
                repeat_threshold, min_size_kb
            )

            print("\n=== Results ===")
            print(f"Total images scanned: {total}")
            print(f"Duplicates removed: {removed}")
            print(f"Unique duplicates archived: {unique}")
            print(f"Cleaned PDF: {output_pdf}")
            if removed > 0:
                print(f"Removed images: {export_zip}")
            success = True
            output_files.append(output_pdf)

        except ValueError:
            print("Invalid number input!")

    elif choice == '2':
        # Page removal
        input_pdf = get_pdf_path()
        if not input_pdf:
            print("No file selected. Exiting.")
            return
        
        input_dir = os.path.dirname(input_pdf)
        input_name = os.path.splitext(os.path.basename(input_pdf))[0]
        output_pdf = os.path.join(input_dir, f"{input_name}_modified.pdf")

        doc = fitz.open(input_pdf)
        total_pages = len(doc)
        doc.close()

        print(f"\nPDF has {total_pages} pages (1-{total_pages})")
        page_input = input("Pages to remove (e.g., '1,3-5,7'): ").strip()
        
        try:
            pages_to_remove = parse_page_range(page_input, total_pages)
            if not pages_to_remove:
                print("No valid pages selected!")
            else:
                print(f"Removing pages: {', '.join(map(str, pages_to_remove))}")
                if remove_pages(input_pdf, output_pdf, pages_to_remove):
                    print(f"Modified PDF saved to:\n{output_pdf}")
                    success = True
                    output_files.append(output_pdf)
        except Exception as e:
            print(f"Error: {e}")

    elif choice == '3':
        # Merge PDFs
        pdf_paths = get_pdf_path(multiple=True)
        if not pdf_paths:
            print("No files selected. Exiting.")
            return
        
        # Save in script's root folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_pdf = os.path.join(script_dir, "merged_final.pdf")
        
        print(f"\nMerging {len(pdf_paths)} PDFs:")
        if merge_pdfs(pdf_paths, output_pdf):
            print(f"\nSuccessfully merged to: {output_pdf}")
            success = True
            output_files.append(output_pdf)
        else:
            print("Failed to merge PDFs.")

    elif choice == '4':
        # Split PDF
        input_pdf = get_pdf_path()
        if not input_pdf:
            print("No file selected. Exiting.")
            return
        
        doc = fitz.open(input_pdf)
        total_pages = len(doc)
        doc.close()

        print(f"\nPDF has {total_pages} pages (1-{total_pages})")
        page_input = input("Enter page ranges to extract (e.g., '4', '7-13', '1-10,12-18'): ").strip()
        
        try:
            page_ranges = []
            for part in re.split(r',', page_input.strip()):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    page_ranges.append((start, end))
                elif part:
                    page = int(part)
                    page_ranges.append((page, page))
            
            # Validate ranges
            valid_ranges = []
            for start, end in page_ranges:
                if 1 <= start <= end <= total_pages:
                    valid_ranges.append((start, end))
                else:
                    print(f"Warning: Range {start}-{end} is invalid for PDF with {total_pages} pages")
            
            if valid_ranges:
                created_files = split_pdf(input_pdf, valid_ranges)
                if created_files:
                    print("\nCreated files:")
                    for file in created_files:
                        print(f"- {file}")
                    success = True
                    output_files.extend(created_files)
            else:
                print("No valid page ranges provided!")
        except Exception as e:
            print(f"Error: {e}")

    elif choice == '5':
        # Special Split
        input_pdf = get_pdf_path()
        if not input_pdf:
            print("No file selected. Exiting.")
            return
        
        doc = fitz.open(input_pdf)
        total_pages = len(doc)
        doc.close()

        print(f"\nPDF has {total_pages} pages (1-{total_pages})")
        page_spec = input("Enter pages to extract (e.g., '1+4+11-16'): ").strip()
        
        output_pdf = special_split_pdf(input_pdf, page_spec)
        if output_pdf:
            print(f"\nCreated new PDF with selected pages: {output_pdf}")
            success = True
            output_files.append(output_pdf)

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nProcessing time: {duration:.2f} seconds")

    if success:
        message = f"Operation completed in {duration:.2f} seconds\n"
        message += "Created files:\n" + "\n".join(output_files)
        showinfo("Done!", message)

if __name__ == "__main__":
    main()