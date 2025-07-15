# PhosphoSitePlus Web Scraper

A Python web scraper that extracts phosphorylation site data from [PhosphoSitePlus.org](https://www.phosphosite.org/) using Playwright. The scraper extracts upstream regulation, downstream regulation, and reference data for phosphorylation sites.

## 🚀 Features

- **Web Scraping**: Automated data extraction from PhosphoSitePlus using Playwright
- **Multiple Data Types**: Extracts upstream regulation, downstream regulation, and references
- **Data Processing**: Explodes and processes complex data structures
- **CSV Export**: Saves data in multiple CSV formats
- **Reference Integration**: Merges PubMed IDs with regulation data
- **Organized Output**: Saves files in protein-specific folders

## 📊 What Data is Extracted

### Upstream Regulation
- Regulatory proteins
- Putative in vivo kinases
- Kinases in vitro
- Phosphatases in vitro

### Downstream Regulation
- Effects of modification on the protein
- Effects of modification on biological processes
- Induced interactions with other proteins
- Inhibited interactions with other proteins

### References
- Reference numbers
- PubMed IDs

### Basic Information
- Amino acid position
- Protein name

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## 📖 Usage

### Command Line Interface

Run the scraper directly from the command line:

```bash
python phospho_group_scraper.py
```

The script will prompt you to enter a SITE_ID (e.g., 2559 for CDK2).

### Example SITE_IDs to Try

- **2559**: CDK2 (Cyclin-dependent kinase 2)
- **1000**: Various proteins
- **5000**: Other phosphorylation sites

## 📁 Output Files

The scraper generates several CSV files:

1. **`phosphorylation_site_{amino_acid}_{protein_name}_upstream.csv`**
   - Upstream regulation data
   - Columns: Upstream regulation, Upstream protein, Organism, References, Amino Acid, Protein

2. **`phosphorylation_site_{amino_acid}_{protein_name}_downstream.csv`**
   - Downstream regulation data
   - Columns: Downstream regulation, Downstream protein, Organism, References, Amino Acid, Protein, Activity

3. **`phosphorylation_site_{amino_acid}_{protein_name}_merged.csv`**
   - Combined upstream and downstream data
   - All regulation data in one file

4. **`phosphorylation_site_{amino_acid}_{protein_name}_references.csv`**
   - Reference data with PubMed IDs
   - Columns: Reference Number, PubMed ID

5. **`{protein_name}/{amino_acid}_{protein_name}.csv`**
   - Final merged data with PubMed IDs
   - Complete dataset with all information

## 🔧 How It Works

### Data Extraction Process

1. **Page Navigation**: Navigates to the PhosphoSitePlus page for the given SITE_ID
2. **Header Extraction**: Extracts protein name and amino acid from the page header
3. **Table Scraping**: Finds and scrapes specific tables:
   - Upstream Regulation table
   - Downstream Regulation table
   - References table
4. **Data Processing**: 
   - Uses regex patterns to extract structured data
   - Explodes complex data structures into individual rows
   - Cleans entity names and reference numbers
5. **Data Merging**: Combines upstream, downstream, and reference data
6. **File Export**: Saves data in multiple CSV formats

### Key Functions

- `first_webscraper()`: Extracts protein name and amino acid
- `upstream_scraper()`: Scrapes upstream regulation data
- `downstream_scraper()`: Scrapes downstream regulation data
- `references_scraper()`: Scrapes reference data
- `main()`: Orchestrates the entire scraping process

## 📋 File Structure

```
├── phospho_group_scraper.py    # Main scraper script
├── requirements.txt             # Python dependencies
├── README.md                   # This file
└── {protein_name}/             # Generated folders
    └── {amino_acid}_{protein_name}.csv
```

## 🐛 Troubleshooting

### Common Issues

**Browser Installation Issues:**
```bash
# Reinstall Playwright browsers
playwright install
```

**Permission Errors:**
- Ensure you have write permissions in the current directory
- Check that the directory is not read-only

**Scraping Errors:**
- Verify the SITE_ID is valid
- Check internet connection
- Ensure PhosphoSitePlus is accessible

**Data Not Appearing:**
- Check console output for debug information
- Verify that the website structure hasn't changed
- Try different SITE_IDs

### Debug Information

The scraper includes debug print statements that show:
- Raw scraped data
- Data processing steps
- DataFrame shapes and contents
- File save confirmations

## 📦 Dependencies

- **playwright**: Browser automation for web scraping
- **pandas**: Data manipulation and CSV export
- **numpy**: Numerical operations
- **asyncio**: Asynchronous programming support
- **re**: Regular expressions for data parsing

## 🔍 Example Output

### Upstream Regulation CSV
```csv
Upstream regulation,Upstream protein,Organism,References,Amino Acid,Protein
Regulatory protein,CDK2,human,"[2559, 2560]",Thr,CDK2
Putative in vivo kinases,PKC,human,"[2561]",Thr,CDK2
```

### Downstream Regulation CSV
```csv
Downstream regulation,Downstream protein,Organism,References,Amino Acid,Protein,Activity
Effects of modification on CDK2,Increased kinase activity,,,"[2559]",Thr,CDK2,Increased kinase activity
Induce interaction with:,Cyclin A,human,"[2560]",Thr,CDK2,
```

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different SITE_IDs
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please respect the terms of service of PhosphoSitePlus.org when using this scraper.

## ⚠️ Disclaimer

This scraper is designed for research and educational purposes. Please:
- Respect the website's robots.txt and terms of service
- Use reasonable request rates
- Don't overload the PhosphoSitePlus servers
- Consider the website's bandwidth and resources

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the debug output in the console
3. Try with different SITE_IDs
4. Ensure all dependencies are properly installed

---

**Note**: The scraper is designed to work with the current structure of PhosphoSitePlus.org. If the website structure changes, the scraper may need updates to continue functioning properly. 