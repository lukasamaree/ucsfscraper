import streamlit as st
import asyncio
import pandas as pd
import os
import tempfile
from phospho_group_scraper import main as scraper_main

# Set page config
st.set_page_config(
    page_title="PhosphoSitePlus Scraper",
    page_icon="🧬",
    layout="wide"
)

# Title and description
st.title("PhosphoSitePlus Web Scraper")
st.markdown("""
This app scrapes phosphorylation site data from PhosphoSitePlus.org.
Enter a SITE_ID to extract upstream regulation, downstream regulation, and reference data.
""")

# Sidebar for input
st.sidebar.header("Input Parameters")
site_id = st.sidebar.text_input(
    "Enter SITE_ID",
    placeholder="e.g., 2559",
    help="Enter the phosphorylation site ID from PhosphoSitePlus"
)

# Main content area
if st.button("🚀 Start Scraping", type="primary"):
    if not site_id:
        st.error("Please enter a SITE_ID")
    else:
        try:
            site_id_int = int(site_id)
            
            # Show progress
            with st.spinner("Scraping data from PhosphoSitePlus..."):
                # Run the scraper
                asyncio.run(scraper_main(site_id_int))
            
            st.success("✅ Scraping completed!")
            
            # Find the generated CSV file
            csv_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".csv") and f"phosphorylation_site_" in file:
                        csv_files.append(os.path.join(root, file))
            
            if csv_files:
                st.subheader("📊 Generated Files")
                
                # Display file information
                for csv_file in csv_files:
                    try:
                        df = pd.read_csv(csv_file)
                        file_info = {
                            "Filename": os.path.basename(csv_file),
                            "Rows": len(df),
                            "Columns": len(df.columns),
                            "File Size": f"{os.path.getsize(csv_file) / 1024:.1f} KB"
                        }
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Filename", file_info["Filename"])
                        with col2:
                            st.metric("Rows", file_info["Rows"])
                        with col3:
                            st.metric("Columns", file_info["Columns"])
                        with col4:
                            st.metric("Size", file_info["File Size"])
                        
                        # Show preview of data
                        st.subheader(f"Preview: {file_info['Filename']}")
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        # Download button
                        with open(csv_file, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {file_info['Filename']}",
                                data=f.read(),
                                file_name=file_info["Filename"],
                                mime="text/csv"
                            )
                        
                        st.divider()
                        
                    except Exception as e:
                        st.error(f"Error reading {csv_file}: {str(e)}")
            else:
                st.warning("No CSV files were generated. Check the console for errors.")
                
        except ValueError:
            st.error("Invalid SITE_ID. Please enter a valid integer.")
        except Exception as e:
            st.error(f"An error occurred during scraping: {str(e)}")

# Add some helpful information
st.markdown("---")
st.markdown("""
### 📋 How to use:
1. Find a phosphorylation site ID from [PhosphoSitePlus](https://www.phosphosite.org/)
2. Enter the SITE_ID in the sidebar
3. Click "Start Scraping" to begin data extraction
4. Download the generated CSV files

### 📊 What data is extracted:
- **Upstream Regulation**: Regulatory proteins, kinases, and phosphatases
- **Downstream Regulation**: Effects of modification on proteins and biological processes
- **References**: PubMed IDs and reference numbers
- **Protein Information**: Amino acid and protein name

### 🔍 Example SITE_IDs to try:
- 2559 (CDK2)
- 1000 (Various proteins)
- 5000 (Other phosphorylation sites)
""")

# Footer
st.markdown("---")
st.markdown("*Powered by Playwright and Streamlit*") 