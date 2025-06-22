# 📑 PDF Tool 1 - Easy PDF Editing for Everyone!

**No technical skills needed!** This simple tool helps you:
- ✂️ Remove unwanted pages from PDFs
- 🖼️ Clean up duplicate images
- 🤝 Combine multiple PDFs
- 🪓 Split large PDFs into smaller parts

## 🏁 Getting Started (3 Easy Steps)

1. **Install** (one-time setup):  
   Just double-click to install Python from [python.org](https://www.python.org/downloads/)  
   Then type in Command Prompt:  
   `pip install PyMuPDF`

2. **Run the Tool**:  
   Double-click `Pdf_Tools.py` or type:  
   `python Pdf_Tools.py`

3. **Follow the Simple Menu**:  
   The program will guide you through every step!

## ✨ What You Can Do

### 🖼️ Remove Duplicate Images
- Automatically finds and removes repeated images
- Keeps one copy of each image
- Saves removed images in a ZIP folder (just in case!)

### ✂️ Edit Pages
- Delete specific pages (like page 5)
- Remove page ranges (like pages 10-20)
- Example input: "1,3-5" removes page 1 and pages 3 through 5

### 🤝 Combine PDFs
- Merge multiple files into one
- Files are combined in alphabetical order
- Perfect for combining scanned documents!

### 🪓 Split PDFs
Two easy ways:
1. **Split by ranges** (creates multiple files)  
   Example: "1-10,11-20" makes two new PDFs

2. **Extract specific pages** (creates one file)  
   Example: "1+3+5-8" makes one PDF with those pages

## 💡 Tips for Best Results
- For image cleaning, try the default settings first (5 repeats, 2KB size)
- When merging, name files like "01_file.pdf", "02_file.pdf" to control order
- All new files save in the same folder as your original PDF
- The program shows how long each operation takes

## ❓ Need Help?
- Video tutorial available at: [github.com/AvroHere/PDF-TOOL-1](https://github.com/AvroHere/PDF-TOOL-1)
- Common issues:
  - If the program doesn't start, make sure Python is installed
  - For large PDFs, be patient - it might take a few minutes

⭐ **Enjoy the tool?** Please star our GitHub repo to support us!
