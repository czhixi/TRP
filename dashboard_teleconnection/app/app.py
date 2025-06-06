from shiny import ui, render, App
# Add MathJax script with additional configuration
mathjax_script = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [['$','$'], ['\\(','\\)']],
      displayMath: [['$$','$$'], ['\\[','\\]']],
      processEscapes: true
    },
    "HTML-CSS": { 
      scale: 100,
      linebreaks: { automatic: true }
    },
    SVG: { 
      linebreaks: { automatic: true } 
    }
  });
</script>
<style>
.math-content {
    padding: 20px;
    line-height: 1.6;
}
.math-content h2 {
    color: #2c3e50;
    margin-top: 20px;
    margin-bottom: 10px;
}
.math-content p {
    margin-bottom: 15px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f5f5f5;
}
</style>
"""


app_ui = ui.page_auto(
    ui.h1("ENSO Teleconnection Maps"),
    ui.input_select(
        "variable",  
        "Select an climate variable below:", 
        {"precip": "Precipitation", 
         "ssr": "Solar Radiation", 
         "temp": "Temperature",
         "snowcover":"Snow Cover"}
    ),

    ui.input_selectize(
        "oscillation",  
        "Select type of oscillation below:",  
        {"lanina":"La Nina", "elnino":"El Nino", "normal": "Neutral"}, 
    ),

    ui.input_select(
        "season",  
        "Select season below:", 
        {"NDJ": "November-December-January",
         "DJF": "December-January-February",
         "JFM": "January-February-March",
         "FMA": "February-March-April",
         "MAM": "March-April-May",
         "AMJ": "April-May-June",
         "MJJ": "May-June-July",
         "JJA": "June-July-August",
         "JAS": "July-August-September",
         "ASO": "August-September-October",
         "SON": "September-October-November",
         "OND": "October-November-December"}
    ),


    ui.card(
        ui.card_header("P-Value"),
        ui.output_ui("pvaluemap", height="100%")
    ),

    ui.card(
        ui.card_header("Seasonal"),
        ui.output_ui("seasonalmap", height="100%")
    ),

    ui.card(
        ui.card_header("Model Details"),
        ui.div(
            {"class": "math-content"},
            ui.HTML("""
            <h3>ENSO Teleconnection Model</h3>
            <p>
                This model builds on studies in weather forecasting and statistical learning, drawing on methodologies and insights. In particular, it is inspired by:
            </p>
            <ol>
                <li>
                    <a href="https://journals.ametsoc.org/view/journals/wefo/35/6/WAF-D-19-0235.1.xml" target="_blank">
                        Seasonal Forecast Skill of ENSO Teleconnection Maps
                    </a>
                </li>
                <li>
                    <a href="https://journals.ametsoc.org/view/journals/bams/82/4/1520-0477_2001_082_0619_ppaawe_2_3_co_2.xml" target="_blank">
                        Probabilistic precipitation anomalies associated with ENSO
                    </a>
                </li>
            </ol>
            <h5>Method</h5>
  <ol>
    <li>
      Identify ENSO events (since 1950) where the ONI anomaly exceeds 0.5°C for at least 5 consecutive months.
    </li>
    <li>
      Compute the relative frequency of below-normal, normal, and above-normal (tercile-defined) precipitation for each land surface grid box, conditioned on ENSO state.
    </li>
    <li>
      Assess the statistical significance of the precipitation signal using a hypergeometric test based on the number of ENSO events and available data years.
    </li>
  </ol>
  
            """)
        )
    )

)

def server(input, output, session):
    @render.ui
    #@render.image(delete_file=True)
    def pvaluemap():
        #response = requests.get(f"https://raw.githubusercontent.com/blackteacatsu/fall_2024_trp_proj/main/scripts/for_kris/outcome/map/{input.variable()}/pvalue_maps_{input.oscillation()}.png")
        #local = f"{input.variable()}/pvalue_maps_{input.oscillation()}.png"
        #if response.status_code == 200:
            #with open(local, "wb") as f:
                #f.write(response.content)

        #print(Path(__file__).parent /'static'/'ENSO Teleconnection Maps'/f'{input.variable()}'/f"pvalue_maps_{input.oscillation()}.png")
        #print(input.variable())
        #print(input.oscillation())
        #img = {'src': f"https://raw.githubusercontent.com/blackteacatsu/fall_2024_trp_proj/main/scripts/for_kris/outcome/map/{input.variable()}/pvalue_maps_{input.oscillation()}.png"}
        return ui.tags.img(src=f"https://raw.githubusercontent.com/blackteacatsu/fall_2024_trp_proj/main/scripts/for_kris/outcome/map/{input.variable()}/pvalue_maps_{input.oscillation()}.png", width = "100%")
    
    @render.ui
    #@render.image(delete_file=True)
    def seasonalmap():
        #print(input.season())
        #print(Path(__file__).parent /'static'/'ENSO Teleconnection Maps'/f'{input.variable()}'/f"prob_{input.oscillation()}_season_{input.season()}.png")
        #img = {"src": f"https://raw.githubusercontent.com/blackteacatsu/fall_2024_trp_proj/main/scripts/for_kris/outcome/map/{input.variable()}/prob_{input.oscillation()}_season_{input.season()}.png", "width": "100%"}  
        return ui.tags.img(src=f"https://raw.githubusercontent.com/blackteacatsu/fall_2024_trp_proj/main/scripts/for_kris/outcome/map/{input.variable()}/prob_{input.oscillation()}_season_{input.season()}.png", width = "100%")

app=App(app_ui, server)