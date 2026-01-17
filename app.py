from flask import Flask, render_template, request, jsonify
from Bio import Entrez
import time

app = Flask(__name__)

# IMPORTANT: NCBI requires you to specify your email address with each request.
# Replace this with your actual email address before running the application.
Entrez.email = "a.student@example.com"


def get_taxonomy_data(organism_names):
    """
    Fetches taxonomy data from NCBI and groups organisms by superkingdom/domain.
    """
    data_by_superkingdom = {}
    failed_organisms = []

    for name in organism_names:
        name = name.strip()
        if not name:
            continue
        try:
            # Step 1: Fetch NCBI data
            handle = Entrez.esearch(db="taxonomy", term=name)
            record = Entrez.read(handle)
            handle.close()
            if not record['IdList']:
                failed_organisms.append(name)
                continue
            taxid = record['IdList'][0]
            time.sleep(0.34)

            handle = Entrez.efetch(db="taxonomy", id=taxid, retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            if not records:
                failed_organisms.append(name)
                continue
            
            record = records[0]
            lineage = record.get('LineageEx', [])
            
            # Step 2: Reliably determine the superkingdom or domain
            superkingdom = "Unknown"
            for tax in lineage:
                if tax['Rank'] == 'superkingdom' or tax['Rank'] == 'domain':
                    superkingdom = tax['ScientificName']
                    break
            
            # Step 3: Initialize data structure
            if superkingdom not in data_by_superkingdom:
                data_by_superkingdom[superkingdom] = {
                    'lineage_map': {superkingdom: ""}, # child: parent map
                    'organisms': []
                }
            
            data_by_superkingdom[superkingdom]['organisms'].append(name)
            
            # Step 4: Merge the current organism's lineage
            parent = superkingdom
            for tax_node in lineage:
                label = tax_node['ScientificName']
                if label == superkingdom:
                    continue
                if label not in data_by_superkingdom[superkingdom]['lineage_map']:
                    data_by_superkingdom[superkingdom]['lineage_map'][label] = parent
                parent = label
            
            organism_label = record['ScientificName']
            if organism_label not in data_by_superkingdom[superkingdom]['lineage_map']:
                data_by_superkingdom[superkingdom]['lineage_map'][organism_label] = parent

        except Exception as e:
            print(f"Error processing '{name}': {e}")
            failed_organisms.append(name)
            continue
            
    # Step 5: Convert to Plotly-ready lists
    final_charts = []
    for sk, data in data_by_superkingdom.items():
        chart_title = f"Domain: {sk}"
        labels = list(data['lineage_map'].keys())
        parents = [data['lineage_map'].get(label, "") for label in labels]

        final_charts.append({
            'title': chart_title,
            'labels': labels,
            'parents': parents,
            'organisms': data['organisms']
        })

    return {'charts': final_charts, 'errors': failed_organisms}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_organisms():
    organism_names = request.json.get('organisms', [])
    result = get_taxonomy_data(organism_names)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
