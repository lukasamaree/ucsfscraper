import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re
import numpy as np
import os



#SITE_ID = 2559  # Change this to scrape a different site

def first_webscraper(page):
    """
    Extracts the protein name and phosphosite from the header, removing (human) from the protein name.
    Returns (amino_acid, protein_name)
    """
    import re
    async def inner():
        amino_acid = None
        protein_name = None
        header_div = await page.query_selector('#titleMainHeader')
        if header_div:
            header_text = await header_div.inner_text()
            # Example: "Phosphorylation Site Page: > Thr160 - CDK2 (human)"
            match = re.search(r'>\s*([A-Za-z0-9]+)\s*-\s*([A-Za-z0-9_\-]+)\s*\(human\)', header_text)
            if match:
                amino_acid = match.group(1)
                protein_name = match.group(2)
            else:
                amino_acid = header_text
                protein_name = header_text
        if protein_name:
            protein_name = re.sub(r'\(human\)', '', protein_name, flags=re.IGNORECASE).replace('(', '').replace(')', '').strip()
        return amino_acid, protein_name
    return inner

async def upstream_scraper(page):
    """
    Scrapes the Upstream Regulation table and returns a dictionary with keys:
    'Regulatory protein', 'Putative in vivo kinases', 'Kinases in vitro', 'Phosphatases in vitro'.
    Each value is a string containing the scraped text for that field.
    """
    result = {
        'Regulatory protein': '',
        'Putative in vivo kinases': '',
        'Kinases in vitro': '',
        'Phosphatases in vitro': ''
    }
    # Find the Upstream Regulation table by its <th> text
    tables = await page.query_selector_all('table')
    for table in tables:
        ths = await table.query_selector_all('th')
        for th in ths:
            th_text = (await th.inner_text()).strip().lower()
            if 'upstream regulation' in th_text:
                # This is the correct table
                trs = await table.query_selector_all('tr')
                for tr in trs:
                    tds = await tr.query_selector_all('td')
                    if len(tds) >= 2:
                        field = (await tds[0].inner_text()).strip().lower()
                        value = (await tds[1].inner_text()).strip()
                        if 'regulatory protein' in field:
                            result['Regulatory protein'] = value
                        elif 'putative in vivo kinases' in field:
                            result['Putative in vivo kinases'] = value
                        elif 'kinases, in vitro' in field:
                            result['Kinases in vitro'] = value
                        elif 'phosphatases, in vitro' in field:
                            result['Phosphatases in vitro'] = value
                return result
    return result

async def downstream_scraper(page, protein_name):
    """
    Scrapes the Downstream Regulation table and returns a dictionary with keys:
    'Effects of modification on {protein_name}',
    'Effects of modification on biological processes',
    'Induce interaction with:',
    'Inhibit interaction with:'.
    Each value is a string containing the scraped text for that field.
    """
    result = {
        f'Effects of modification on {protein_name}': '',
        'Effects of modification on biological processes': '',
        'Induce interaction with:': '',
        'Inhibit interaction with:': ''
    }
    # Find the Downstream Regulation table by its <th> text
    tables = await page.query_selector_all('table')
    for table in tables:
        ths = await table.query_selector_all('th')
        for th in ths:
            th_text = (await th.inner_text()).strip().lower()
            if 'downstream regulation' in th_text:
                # This is the correct table
                trs = await table.query_selector_all('tr')
                for tr in trs:
                    tds = await tr.query_selector_all('td')
                    if len(tds) >= 2:
                        field = (await tds[0].inner_text()).strip().lower()
                        value = (await tds[1].inner_text()).strip()
                        field_clean = field.strip().rstrip(':').strip()
                        if field_clean == f'effects of modification on {protein_name.lower()}':
                            result[f'Effects of modification on {protein_name}'] = value
                        elif field_clean == 'effects of modification on biological processes':
                            result['Effects of modification on biological processes'] = value
                        elif 'induce interaction with' in field:
                            result['Induce interaction with:'] = value
                        elif 'inhibit interaction with' in field:
                            result['Inhibit interaction with:'] = value
                return result
    return result

async def references_scraper(page):
    """
    Scrapes the References table and returns a list of dicts with keys 'Reference Number' and 'PubMed ID'.
    """
    results = []
    # Find the References table by its <th> text
    tables = await page.query_selector_all('table')
    for table in tables:
        ths = await table.query_selector_all('th')
        for th in ths:
            th_text = (await th.inner_text()).strip().lower()
            if th_text == 'references':
                # This is the correct table
                trs = await table.query_selector_all('tr')
                for tr in trs:
                    tds = await tr.query_selector_all('td')
                    if len(tds) >= 2:
                        # Reference number is in the first column
                        ref_number = (await tds[0].inner_text()).strip()
                        # PubMed ID is the first number in the second column (bold red)
                        pubmed_match = re.search(r'(\d{7,})', await tds[1].inner_text())
                        pubmed_id = pubmed_match.group(1) if pubmed_match else None
                        results.append({
                            'Reference Number': ref_number,
                            'PubMed ID': pubmed_id
                        })
                return results
    return results

async def main(site_id):
    url = f"https://www.phosphosite.org/siteAction.action?id={site_id}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('domcontentloaded')
        amino_acid, protein_name = await first_webscraper(page)()
        data = [{
            'Amino Acid': amino_acid,
            'Protein': protein_name
        }]
        filename = f'phosphorylation_site_{amino_acid}_{protein_name}.csv'
        df = pd.DataFrame(data)
        #df.to_csv(filename, index=False)
        #print(f"Saved {filename}")
        # Save upstream scraper result, exploded with entity, organism, references
        upstream_data = await upstream_scraper(page)
        print(f"DEBUG: Upstream data scraped: {upstream_data}")
        exploded_rows = []
        entity_pattern = re.compile(r'([A-Za-z0-9\-_,\[\] ]+?)\s*\((human|mouse)\)\s*\(([^\)]+)\)')
        for field, value in upstream_data.items():
            print(f"DEBUG: Processing field '{field}' with value: '{value}'")
            # Find all matches like NAME (organism) ( numbers )
            for match in entity_pattern.finditer(value):
                entity = match.group(1).strip()
                organism = match.group(2).strip()
                references = [int(ref.strip()) for ref in match.group(3).split(',') if ref.strip().isdigit()]
                exploded_rows.append({
                    'Field': field,
                    'Entity': entity,
                    'Organism': organism,
                    'References': references,
                    'Amino Acid': amino_acid,
                    'Protein': protein_name
                })
                print(f"DEBUG: Added row - Entity: {entity}, Organism: {organism}, References: {references}")
        upstream_df = pd.DataFrame(exploded_rows)
        print(f"DEBUG: Upstream DataFrame shape: {upstream_df.shape}")
        print(f"DEBUG: Upstream DataFrame columns: {upstream_df.columns.tolist()}")
        if not upstream_df.empty:
            print(f"DEBUG: Upstream DataFrame head:\n{upstream_df.head()}")
            upstream_df['Entity'] = upstream_df['Entity'].str.lstrip(', ').str.strip()
            upstream_df = upstream_df.rename(columns={
                'Entity': 'Upstream protein',
                'Field': 'Upstream regulation'
            })
        upstream_filename = f'phosphorylation_site_{amino_acid}_{protein_name}_upstream.csv'
        # print(f"Saved {upstream_filename}")
        # Save downstream scraper result, fully exploded
        downstream_data = await downstream_scraper(page, protein_name)
        exploded_downstream_rows = []
        # Regex for effect phrase and references
        effect_pattern = re.compile(r'([^\(]+?)\s*\(([^\)]+)\)')
        entity_pattern = re.compile(r'([A-Za-z0-9\-_,\[\] ]+?)\s*\((human|mouse)\)\s*\(([^\)]+)\)')
        # Explode the first two fields using regex
        for field in [f'Effects of modification on {protein_name}', 'Effects of modification on biological processes']:
            value = downstream_data.get(field, '')
            for match in effect_pattern.finditer(value):
                effect = match.group(1).strip()
                references = [int(ref.strip()) for ref in match.group(2).split(',') if ref.strip().isdigit()]
                exploded_downstream_rows.append({
                    'Downstream regulation': field,
                    'Downstream protein': effect,
                    'Organism': '',
                    'References': references,
                    'Amino Acid': amino_acid,
                    'Protein': protein_name
                })
        # Explode the last two fields as before
        for field in ['Induce interaction with:', 'Inhibit interaction with:']:
            value = downstream_data.get(field, '')
            for match in entity_pattern.finditer(value):
                protein = match.group(1).strip()
                organism = match.group(2).strip()
                references = [int(ref.strip()) for ref in match.group(3).split(',') if ref.strip().isdigit()]
                exploded_downstream_rows.append({
                    'Downstream regulation': field,
                    'Downstream protein': protein,
                    'Organism': organism,
                    'References': references,
                    'Amino Acid': amino_acid,
                    'Protein': protein_name
                })
        downstream_df = pd.DataFrame(exploded_downstream_rows)
        if downstream_df.empty:
            columns = ['Downstream regulation', 'Downstream protein', 'Organism', 'References', 'Amino Acid', 'Protein', 'Activity']
            downstream_df = pd.DataFrame([{col: float('nan') for col in columns}])
        else:
            downstream_df['Downstream protein'] = downstream_df['Downstream protein'].str.lstrip(', ').str.strip()
            downstream_df['Activity'] = None
            mask_effect = downstream_df['Downstream regulation'].str.startswith('Effects of')
            mask_protein = ~mask_effect
            downstream_df.loc[mask_effect, 'Activity'] = downstream_df.loc[mask_effect, 'Downstream protein']
            downstream_df.loc[mask_effect, 'Downstream protein'] = None
            downstream_df.loc[mask_protein, 'Activity'] = None
            # Replace all empty strings and None with np.nan
            downstream_df = downstream_df.replace({None: np.nan, '': np.nan})
        downstream_filename = f'phosphorylation_site_{amino_acid}_{protein_name}_downstream.csv'
      #  downstream_df.to_csv(downstream_filename, index=False, na_rep='nan')
       # print(f"Saved {downstream_filename}")
        # Merge downstream and upstream DataFrames and save as a new CSV
        # Align columns, filling missing columns with NaN as needed
        # Add missing columns to upstream_df to match downstream_df
        for col in downstream_df.columns:
            if col not in upstream_df.columns:
                upstream_df[col] = np.nan
        for col in upstream_df.columns:
            if col not in downstream_df.columns:
                downstream_df[col] = np.nan
        merged_df = pd.concat([downstream_df, upstream_df], ignore_index=True, sort=False)
        merged_filename = f'phosphorylation_site_{amino_acid}_{protein_name}_merged.csv'
        # merged_df.to_csv(merged_filename, index=False, na_rep='nan')
        # print(f"Saved {merged_filename}")
        references = await references_scraper(page)
        if references:
            ref_df = pd.DataFrame(references)
            ref_df['Reference Number'] = ref_df['Reference Number'].astype(str)
            ref_filename = f'phosphorylation_site_{amino_acid}_{protein_name}_references.csv'
            #ref_df.to_csv(ref_filename, index=False)
            # Explode the References column, keeping NaN rows
            if 'References' in merged_df.columns:
                merged_exploded = merged_df.copy()
                merged_exploded = merged_exploded.explode('References', ignore_index=True)
                # If References is NaN, Reference Number will also be NaN
                merged_exploded['Reference Number'] = merged_exploded['References'].astype('str')
                # For NaN, astype('str') gives 'nan', which will not match any reference, so merge will keep those rows with NaN PubMed ID
                merged_with_pubmed = pd.merge(
                    merged_exploded,
                    ref_df,
                    on='Reference Number',
                    how='left'
                )
                # (Optional) If you want to display empty PubMed ID as 'nan' in the CSV
                folder = protein_name
                os.makedirs(folder, exist_ok=True)
                merged_with_pubmed_filename = os.path.join(folder, f'{amino_acid}_{protein_name}.csv')
                merged_with_pubmed.to_csv(merged_with_pubmed_filename, index=False, na_rep='nan')
                print(f"Saved {merged_with_pubmed_filename}")


if __name__ == "__main__":
    site_id = input("Enter SITE_ID (e.g., 2559): ")
    try:
        site_id = int(site_id)
    except ValueError:
        print("Invalid SITE_ID. Please enter an integer.")
        exit(1)
    asyncio.run(main(site_id)) 