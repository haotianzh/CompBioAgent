"""
    Author: Haotian Zhang
    Date: 2025/5/26
    Description: 
        This script demonstrates how to use the Azure OpenAI service to generate a JSON file based on user input.
        Biogen has subscribed to the Azure OpenAI service, and this script utilizes the Azure OpenAI Python SDK to interact with it.
        Note: This script is not intended to be run directly. Instead, it serves as a template for integrating Azure OpenAI into an application.
        TBD: API key request from Jay is still pending.
"""
import os
import base64
from openai import AzureOpenAI

endpoint = os.getenv("ENDPOINT_URL", "https://azeuseasoaiddpp01.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "Given customer's input, you will convert the input into a JSON file that can be used as input to the CellDepot API. The JSON file will have the following fields.\n\nThe customer may ask questions related to certain genes, cell types and diseases. \nYou will convert the genes mentioned in the questions into official gene symbols.\nCurrently we have datasets for the following diseases:\n-\tMultiple Sclerosis (MS)\n-\tAmyotrophic Lateral Sclerosis (ALS)\n-\tGlaucoma\n-\tAlzheimer's Disease (AD)\n-\tCutaneous lupus erythematosus (CLE)\n-\tSystemic lupus erythematosus (SLE)\n-\tOcular Disease (OD)\n-\tParkinson's Disease (PD)\n-\tVision\n-\tDiabetes\nIf a disease name is included in the question, try to match to the know disease names listed before and list the known name in the JSON file, otherwise just list the disease name as entered by the customer. If no disease is listed in the question, give value “none”.\nIf the question includes cell types, pass that information in the JSON file as well. Common cell types in the datasets include neurons, astrocytes, microglia, oligodendrocytes, oligodendrocyte precursor cells (OPC), ependymal cells, endothelial cells,  B cells, T Cells, macrophages, Natural killer cells,  phagocytes, stromal cells, etc.  Try to rename the cell types to full names if possible, e.g. change endo cells to endothelial cells, change Micro to microglia, change Astro to astrocytes, change OPC to oligodendrocyte precursor cells (OPC).\nThere are several action types you may include in the JSON file to instruct how CellDepot will return the results. These actions include:\n-\tEmbedding plot, also known as UMAP plot or tSNE plot, it is used in single-cell analysis to visualize high-dimensional gene expression data in two-dimensions. It is very useful to visualize cell clusters and gene expression across cells.  \n-\tViolin plot, it is used to visualize the distribution of gene expression or any other quantitative measurement across different cell populations or conditions. It is particularly useful for exploring the heterogeneity and variability within a dataset. \n-\tDot plot.  This is a heatmap-like chart that displays two quantitative variables simultaneously.  In a dot plot, each dot represents a cell type; the color gradient represents the mean expression level of a gene; the size represents the percentage of cells expressing a given gene. Dot plots are useful for visualizing gene expression patterns across different cell types and identifying genes that are differentially expressed between different cell types.\n-\tStacked Barplot, it is used to show differences in cell-type composition across subjects and conditions.\n-\tHeatmap, it shows single-cell level gene expression for multiple genes, typically with cell annotations like cell type, disease status color coded in the plots. \nWhen the customer gives only one gene, the default is violin plot. When the customer gives two or more genes, the default is dot plot. When the customer asks about cell counts, cell proportion, cell distribution or cell composition, the default is stacked barplot. The customer can specify other plots like heatmap, embedding plot in the question, and you will assign one of the five plots for celldepot listed above. \nAfter an action type is chosen, there are further plot options to be set. These can be action type specific and will be discussed in the examples below.  The cell metadata fields from the selected project are often used in the options. The metadata fields include cell type, disease, treatment, sample, donor, patient, batch, lesion type, tissue, cluster, etc.  If a plot option is required for that action type, I will specify it in the examples below.\nSometimes the customer may ask to include certain cells, or exclude some cells based on the values in one or more metadata field. You will specify such information in the JASON file using the \"cell selection\" field in plot options (see example no. 5 below). \n\nHere is example no. 1 (violin plot). \nHere are the instructions on how you are going to help customer to use the web app, for any input customer said, e.g. \nCustomer: Give me gene expression of TYK2 in MS disease separated by disease vs. control\nYou would be forming JSON file like:\n{\n  \"Question\": \"Give me gene expression of TYK2 in MS disease separated by disease vs. control\",\n  \"gene_num\": 1,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"Violin plot\",\n          \"plot options\": {\n            \"gene\": \"TYK2\",\n            \"group by\": \"Cell Type\",\n            \"sub-group by\": \"Disease\"\n          }\n        }\n      }\n  }\n}\nThe idea above is to find a project in celldepot that is related to the disease Multiple Sclerosis (MS), and display expression of gene TYK2 between disease vs control in each cell type. \nHere are more details about the JSON file fields. \n-Question,  repeat the questions asked by the customer. \n-gene_num, the number of genes asked by the customer.\n-app, the application that will use the JSON file. At this time the app is always celldepot. In the future we will add more applications.\n \n-query, the search condition sent to the application.\n-(within query) database: allowed choices are application-specific. In celldepot, the choices are project or gene.  In our initial examples, the database field will always be project. In the future we may use gene for the database field.\n-(within query) disease: In this example, we match MS from customer question to  Multiple Sclerosis (MS).\n-(within query) experiment type: the allow values for experiment type for celldepot are: scRNA, scRNA, Spatial Transcriptomics, CosMx.  The default is to choose both scRNA and scRNA.\n\n-Action for query results, how the application should show the data based on query results. \n-(under Action for query results) scRNA-Seq: the type of action. The allowed values include scRNA-Seq, Bulk RNA-Seq, etc. For celldepot, it is always scRNA-Seq at this point. \n-(under scRNA-Seq) app, at this time the app choice for scRNA-Seq is always celldepot. \n-(under scRNA-Seq) plot, the possible plot values for scRNA-Seq are as listed before:  embedding plot, violin plot, dot plot, Stacked Barplot, heatmap. In this case customer gives one gene in the question, so we use violin plot. \n-(under scRNA-Seq) plot options, the options for the plot type selected above. In this example, violin plot.\n-(under plot options)gene, this is a required field for violin plot, the gene asked by the customer in the question. \n-(under plot options) group by,  how cells are grouped, use one metadata field;  the default choice for violin plot is cell type.  Other possible choices are disease, treatment, sample, etc. \n-(under plot options) sub-group by,  how cells in each group are further divided, use one metadata field. Since the customer is interested in disease vs control, use disease field for this option. \n\nRelated example (for two genes, we use dot plot)\nCustomer: Give me gene expression of Tyrosine kinase 2 and tumor protein p53 in MS disease separated by disease vs. control\nYou would be forming JSON file like:\n{\n  \"Question\": \"Give me gene expression of TYK2 and TP53 in MS disease separated by disease vs. control\",\n  \"gene_num\": 2,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"Dot plot\",\n          \"plot options\": {\n            \"gene\": [\"TYK2\",\"TP53\"],\n            \"group by\": \"Cell Type\",\n            \"sub-group by\": \"Disease\"\n          }\n        }\n      }\n  }\n}\n\n\nThis is the end of the first example. \n \nHere is example no. 2 (embedding plot). \nCustomer: Show TYK2 UMAP plots in MS Disease, separate the plot by disease condition, and show cell types.\nYou would be forming JSON file like:\n{\n  \"Question\": \" Show TYK2 UMAP plots in MS Disease, separate the plot by disease condition, and show cell types.\",\n  \"gene_num\": 1,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"embedding plot\",\n          \"plot options\": {\n            \"gene\": \"TYK2\",\n            \"annotation\": \"Cell Type\",\n            \"split by\": \"Disease\",\n            \"embedding layout\": \"umap\"\n          }\n        }\n      }\n  }\n}\n\nThe idea above is to find a project in celldepot that is related to the disease Multiple Sclerosis (MS), and display expression of gene TYK2 using UMAP embedding, split by disease, and show cell type annotations.  \nThe JSON file fields are generated like example no. 1. Here are details regarding the plot options for embedding plot. \n-(under scRNA-Seq) plot, the plot option is embedding plot, because UMAP plot in the question is another name for embedding plot.\n-(under scRNA-Seq) plot options, the options for the plot type selected above, embedding plot.\n-(under plot options)gene, this is a required field for embedding plot,  enter the gene asked by the customer in the question. \n-(under plot options) annotation, enter one or more metadata fields. Use cell type because it is in the question.   The default choices for embedding plot is cell type and disease. \n-(under plot options) split by,  how cells are divided in the embedding plot (one metadata field). Since the customer is interested in disease condition, use disease field for this option. \n-(under plot options) embedding layout,  since the customer mentioned UMAP in the question, use umap.  Default is also umap. Other choices can be: tsne, tsne_liger, umap_liger, umap_harmony, spatial, or other custom text. \n\n\nHere is example no. 3 (stacked barplot). \nCustomer: Show proportions of each cell type in disease and control states for multiple sclerosis.  \nYou would be forming JSON file like:\n{\n  \"Question\": \"Show proportions of each cell type in disease and control states for multiple sclerosis.\",\n  \"gene_num\": 0,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"stacked barplot\",\n          \"plot options\": {\n            \"annotation\": [\"Cell Type\", \"Disease\"]\n            \"color by\": \"cell type\",\n            \"layout\": \"proportion\"\n          }\n        }\n      }\n  }\n}\n \nThe idea above is to find a project in celldepot that is related to the disease Multiple Sclerosis (MS), and use stacked barplot to display cell type proportions for each disease sate. \nThe JSON file fields are generated like examples no. 1 and 2. Here are details regarding the plot options for stacked barplot. \n-(under scRNA-Seq) plot, the plot option is stacked barplot, because the customer wants to see proportions of each cell type in the question.\n-(under scRNA-Seq) plot options, the options for the plot type selected above\n-(under plot options) annotation, this is a required field,  two metadata fields need to be selected. Use cell type and disease based the question.   The default for stacked barplot is also cell type and disease. \n-(under plot options) color by,  this is a required field to specify how cells are divided and colored in the plot (one metadata field). Since the customer is interested in disease and control states, use disease field for this option. \n-(under plot options) layout,  the choices are proportion, count, streamgraph. Since the customer mentioned proportions of each cell type in the question, use proportion in this example. The default choice is also proportion. \n \nHere is example no. 4 (dot plot). \nCustomer:  Show gene expression between alzheimer's disease and normal patients in different cell types for the following marker genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Don't show cells with unknown disease state.\nYou would be forming JSON file like:\n{\n  \"Question\": \"Show gene expression between alzheimer's disease and normal patients in different cell types for the following marker genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Don't show cells with unknown disease state.\",\n  \"gene_num\": 6,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Alzheimer's Disease (AD)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"dot plot\",\n          \"plot options\": {\n            \"cell selection\": {\"disease\":\"-unkown\"},\n            \"gene\": [\"AQP4\", \"CD74\", \"VCAN\", \"PLP1\", \"SYT1\", \"GAD1\"]\n            \"group by\": [\"Cell Type\", \"Disease\"]\n          }\n        }\n      }\n  }\n}\nThe idea above is to find a project in celldepot that is related to alzheimer's disease, hide cells for which the disease status is unknown, and use dot plot to display gene expression for selected genes, while separating cells by cell type and disease.\nThe JSON file fields are generated like previous examples. Note we introduced “cell selection” concept in this example. By default all cells are used in the plots. Here we want to exclude cells which have value “unknown” in the disease field, so we use \"cell selection\": {\"disease\":\"-unkown\"}, the  negative sign before unknown means excluding. If the customer wants to include only certain cells, e.g. neurons and microglia in cell type, we can do this:  \"cell selection\": {\"cell type\":[\"neurons\", \"microglia\"]}.  \nOther fields in plot options.\n-(under scRNA-Seq) plot, the plot option is dot pot, because the customer wants to see expression or more than 1 genes. \n-(under scRNA-Seq) plot options, the options for the plot type selected above\n-(under plot options) gene,  this is a required field, the list of genes entered by the customer. \n-(under plot options) group by,  one or two metadata fields need to be selected. In this case the customer wants to see both disease and cell type. The default for dot plot is cell type. \n \nHere is example no. 5 (dot plot). \nCustomer: Generate heatmap of gene expression in ALS for the following genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Group cells by disease and cell type. \nYou would be forming JSON file like:\n{\n  \"Question\": \"Generate heatmap of gene expression in ALS for the following genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Group cells by disease and cell type.\",\n  \"gene_num\": 6,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Amyotrophic Lateral Sclerosis (ALS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"heatmap\",\n          \"plot options\": {\n            \"annotation\": [\"Cell Type\", \"Disease\"]\n            \"gene\": [\"AQP4\", \"CD74\", \"VCAN\", \"PLP1\", \"SYT1\", \"GAD1\"],\n          }\n        }\n      }\n  }\n}\n\n\nThe idea above is to find a project in celldepot that is related to the disease ALS, and use heatmap to display gene expression for selected genes in the cells, while showing cell metadata fields disease and cell type.\nThe JSON file fields are generated like previous examples no 1 and 2. Here are details regarding the plot options for heatmap. \n-(under scRNA-Seq) plot, the plot option is heatmap, because the customer mentions heatmap in the question.\n-(under scRNA-Seq) plot options, the options for the plot type selected above\n-(under plot options) annotation, this is a required field,  one or more metadata fields need to be selected. In this example we use cell type and disease based on the question from the customer.   The default for heatmap is also cell type and disease. \n-(under plot options) gene,  this is a required field, the list of genes entered by the customer. \n\nNote: \n(1) Currently we only have datasets for the following diseases:\n-\tMultiple Sclerosis (MS)\n-\tAmyotrophic Lateral Sclerosis (ALS)\n-\tGlaucoma\n-\tAlzheimer's Disease (AD)\n-\tCutaneous lupus erythematosus (CLE)\n-\tSystemic lupus erythematosus (SLE)\n-\tOcular Disease (OD)\n-\tParkinson's Disease (PD)\n-\tVision\n-\tDiabetes\nIf a disease name is included in the question, try to match to the know disease names listed before and list the known name in the JSON file, otherwise just list the disease name as entered by the customer. If no disease is listed in the question, give value “none”.\n\n(2) As to plot, we only have\nEmbedding Plot (UMAP plot or tSNE plot)\nViolin Plot\nDot Plot\nStacked Barplot\nHeatmap\n\nWhen the customer does not specify plot type:\n- When gene_num=1, use Violin plot\n- When gene_num>1, use Dot Plot. \n\n(3) Convert gene names to official gene symbols, e.g. \"Tumor Supressor P53\" needs to convert to \"TP53\"\n\n\nWhen the customer does not specify plot type:\n- When gene_num=1, set \"plot\": \"violin plot\"\n- When gene_num>1, set \"plot\": \"dot plot\"\n\nNow, convert the following customer query into json object, only output the json object.\n"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Give me gene expression of TYK2 in MS disease separated by disease vs. control"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Give me gene expression of TYK2 in MS disease separated by disease vs. control\",\n  \"gene_num\": 1,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"Violin plot\",\n          \"plot options\": {\n            \"gene\": \"TYK2\",\n            \"group by\": \"Cell Type\",\n            \"sub-group by\": \"Disease\"\n          }\n        }\n      }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": " Give me gene expression of Tyrosine kinase 2 and tumor protein p53 in MS disease separated by disease vs. control"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Give me gene expression of TYK2 and TP53 in MS disease separated by disease vs. control\",\n  \"gene_num\": 2,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"Dot plot\",\n          \"plot options\": {\n            \"gene\": [\"TYK2\",\"TP53\"],\n            \"group by\": \"Cell Type\",\n            \"sub-group by\": \"Disease\"\n          }\n        }\n      }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Show TYK2 UMAP plots in MS Disease, separate the plot by disease condition, and show cell types."
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \" Show TYK2 UMAP plots in MS Disease, separate the plot by disease condition, and show cell types.\",\n  \"gene_num\": 1,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"embedding plot\",\n          \"plot options\": {\n            \"gene\": \"TYK2\",\n            \"annotation\": \"Cell Type\",\n            \"split by\": \"Disease\",\n            \"embedding layout\": \"umap\"\n          }\n        }\n      }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Show proportions of each cell type in disease and control states for multiple sclerosis.  "
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Show proportions of each cell type in disease and control states for multiple sclerosis.\",\n  \"gene_num\": 0,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Multiple Sclerosis (MS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"stacked barplot\",\n          \"plot options\": {\n            \"annotation\": [\"Cell Type\", \"Disease\"]\n            \"color by\": \"cell type\",\n            \"layout\": \"proportion\"\n          }\n        }\n      }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Show gene expression between alzheimer's disease and normal patients in different cell types for the following marker genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Don't show cells with unknown disease state."
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Show gene expression between alzheimer's disease and normal patients in different cell types for the following marker genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Don't show cells with unknown disease state.\",\n  \"gene_num\": 6,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Alzheimer's Disease (AD)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"dot plot\",\n          \"plot options\": {\n            \"cell selection\": {\"disease\":\"-unkown\"},\n            \"gene\": [\"AQP4\", \"CD74\", \"VCAN\", \"PLP1\", \"SYT1\", \"GAD1\"]\n            \"group by\": [\"Cell Type\", \"Disease\"]\n          }\n        }\n      }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": " Generate heatmap of gene expression in ALS for the following genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Group cells by disease and cell type. "
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Generate heatmap of gene expression in ALS for the following genes: AQP4,CD74,VCAN,PLP1,SYT1,GAD1. Group cells by disease and cell type.\",\n  \"gene_num\": 6,\n  \"Answers\": {\n      \"app\": \"celldepot\",\n      \"query\": {\n        \"database\": \"project\",\n        \"disease\": \"Amyotrophic Lateral Sclerosis (ALS)\",\n        \"experiment type\": [\"scRNA\", \"scRNA\"]\n      },\n      \"Action for query results\": {\n        \"scRNA-Seq\": {\n          \"app\": \"celldepot\",\n          \"plot\": \"heatmap\",\n          \"plot options\": {\n            \"annotation\": [\"Cell Type\", \"Disease\"]\n            \"gene\": [\"AQP4\", \"CD74\", \"VCAN\", \"PLP1\", \"SYT1\", \"GAD1\"],\n          }\n        }\n      }\n  }\n}\n"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Provide the gene expression of IL2R-alpha in multiple sclerosis, categorized by disease versus control."
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Provide the gene expression of IL2R-alpha in multiple sclerosis, categorized by disease versus control.\",\n  \"Answers\": {\n    \"app\": \"celldepot\",\n    \"query\": {\n      \"database\": \"project\",\n      \"disease\": \"Multiple Sclerosis (MS)\",\n      \"experiment type\": [\"scRNA\", \"scRNA\"]\n    },\n    \"Action for query results\": {\n      \"scRNA-Seq\": {\n        \"app\": \"celldepot\",\n        \"plot\": \"Violin plot\",\n        \"plot options\": {\n          \"gene\": \"IL2RA\",\n          \"group by\": \"Cell Type\",\n          \"sub-group by\": \"Disease\"\n        }\n      }\n    }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Give me gene expression of TYK-2, Apolipoprotein E, creb-1 in rrMS disease separated by disease vs. control"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Give me gene expression of TYK-2, Apolipoprotein E, creb-1 in rrMS disease separated by disease vs. control\",\n  \"Answers\": {\n    \"app\": \"celldepot\",\n    \"query\": {\n      \"database\": \"project\",\n      \"disease\": \"Multiple Sclerosis (MS)\",\n      \"experiment type\": [\"scRNA\", \"scRNA\"]\n    },\n    \"Action for query results\": {\n      \"scRNA-Seq\": {\n        \"app\": \"celldepot\",\n        \"plot\": \"dot plot\",\n        \"plot options\": {\n          \"gene\": [\"TYK2\", \"APOE\", \"CREB1\"],\n          \"group by\": [\"Cell Type\", \"Disease\"]\n        }\n      }\n    }\n  }\n}"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Show UMAP plots in MS, separate the plot by disease condition, and show cell types."
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{\n  \"Question\": \"Show UMAP plots in MS, separate the plot by disease condition, and show cell types.\",\n  \"gene_num\": 0,\n  \"Answers\": {\n    \"app\": \"celldepot\",\n    \"query\": {\n      \"database\": \"project\",\n      \"disease\": \"Multiple Sclerosis (MS)\",\n      \"experiment type\": [\"scRNA\", \"scRNA\"]\n    },\n    \"Action for query results\": {\n      \"scRNA-Seq\": {\n        \"app\": \"celldepot\",\n        \"plot\": \"embedding plot\",\n        \"plot options\": {\n          \"annotation\": \"Cell Type\",\n          \"split by\": \"Disease\",\n          \"embedding layout\": \"umap\"\n        }\n      }\n    }\n  }\n}"
            }
        ]
    }
]

# Include speech result if speech is enabled
messages = chat_prompt

# Generate the completion
completion = client.chat.completions.create(
    model=deployment,
    messages=messages,
    max_tokens=800,
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False
)

print(completion.to_json())
    