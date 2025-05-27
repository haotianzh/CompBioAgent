from openai import OpenAI
from prompt import chat_prompt
from plot_h5ad import plot
import json 
import scanpy as sc
import os

APP_NAME = "CompBioAgent: "

class CompBioAgent:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        # example of a tool definition
        self.tools = [{
            "type": "function",
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia"
                    }
                },
                "required": [
                    "location"
                ],
                "additionalProperties": False
            }
        }]
        self.clear()

    def clear(self):
        self.history = chat_prompt
        self.datasets = []

    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content
        }
        self.history.append(message)

    def get_response(self, model="gpt-4.1", tools=None):
        response = self.client.responses.create(
            model=model,
            input=self.history,
            tools=tools
        )
        return response
    
    def add_tool(self, tool):
        self.tools.append(tool)

    def check_dataset(self, filename):
        if not os.path.exists(filename):
            return "Dataset file does not exist."
        try:
            adata = sc.read(filename)
            self.datasets.append(adata)
            return f"Dataset {filename} loaded successfully with {adata.n_obs} observations and {adata.n_vars} variables."
        except Exception as e:
            return f"Error loading dataset: {str(e)}"


    def tool_calling(self, params):
        pass


    def logic(self, response):
        if "Answers" not in response:
            print(APP_NAME, "Response must contain 'Answers' key.\n")
        answers = response["Answers"]
        if answers['query']['database'] == 'project':
            print(APP_NAME, f'not implemented yet!\n')
        else:
            print(APP_NAME, "loading dataset...\n")
            self.check_dataset(answers['query']['database'])
            print(APP_NAME, f"Dataset {answers['query']['database']} is now available for analysis.\n")
            plot_type = answers['Action for query results']['scRNA-Seq']['plot']
            print(APP_NAME, f"Plot type: {plot_type}\n")
            plot_options = answers['Action for query results']['scRNA-Seq']['plot options']
            if plot_type == 'dot plot':
                if 'gene' in plot_options:
                    gene = plot_options['gene']
                    group = plot_options['group by']
                    if group == 'Cell Type': # rename for in-house dataset
                        group = 'cell_type'
                    print(f"Generating dot plot for gene {gene} grouped by {group}.\n")
                    json_data = {
                        "h5ad": answers['query']['database'],
                        "genes": gene,
                        "groups": {group: []},
                        "plot": "dotplot",
                        "var_col": "feature_name",
                        "options":{
                            "img_width" : 15,
                            "img_height" : 5,
                            "dotsize": 2,
                            "cutoff": 0.1,
                            "palette" : "Set3",
                            "img_format": "png",
                            "img_id": "",
                            "img_html": True
                            }
                        }
                    print(json_data)
                    print(APP_NAME, "Plotting...\n")
                    html = plot(json_data)
                    with open("dotplot.html", "w") as f:
                        f.write(html)
                    print(APP_NAME, "Dot plot saved to dotplot.html.\n")
                
            
    def start(self):
        print(APP_NAME, "Welcome to the CompBioAgent! Type 'exit' or 'quit' to stop.\n")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            self.add_message("user", user_input)
            response = self.get_response(tools=self.tools).output[0].content[0].text
            bot_reply = json.loads(response)
            self.logic(bot_reply)
            # print(f"CompBioAgent: {bot_reply}")
            self.add_message("assistant", response)


if __name__ == "__main__":
    # Replace with your actual OpenAI API key
    api_key = "your_openai_api_key_here"
    agent = CompBioAgent(api_key)
    agent.start()
    # test example
    # show me the expression of TP53 and P10 in /edgehpc/dept/compbio/data/shared/CartaBio/h5ad/1.h5ad