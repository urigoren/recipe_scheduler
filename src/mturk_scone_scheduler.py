import collections, itertools, json, re, operator
from functools import reduce
from pathlib import Path
import pandas as pd

data_dir = Path(__file__).absolute().parent.parent /"data"/"scone"
output_file = Path(__file__).absolute().parent.parent /"mturk"/"scone_scheduler_mturk.html"

parsed = []
with (data_dir / "alchemy-dev.tsv").open('r') as f:
    for line in f:
        idx, *parts = line.strip().split('\t')
        states       = [{int(v.split(':',1)[0]):v.split(':')[1].strip() for v in p.split(' ')} for i,p in enumerate(parts) if i%2==0]
        instructions = [p for i,p in enumerate(parts) if i%2==1]
        instructions.insert(0,"INIT")
        seq = 0
        for state, instruction in zip(states,instructions):
            d = state
            d["instruction"]=instruction
            d['id']=idx
            d['seq']=seq
            parsed.append(d)
            seq+=1
df = pd.DataFrame(parsed)

beakers = reduce(operator.or_, [set(df[i].unique()) for i in range(1,8)], set())
colors = {c for b in beakers for c in b}



def block(row,beaker):
    ccc = ("www"+row[beaker].replace("_",""))[-3:]
    colors = {}
    for i,c in enumerate(ccc):
        colors[i]={
            "w":"white",
            "r":"red",
            "b":"brown",
            "y":"yellow",
            "p":"purple",
            "o":"orange",
            "g":"green",
        }[c]
    return f"""
    <table style="border: 1px solid black;">
    <tr style="border: 1px solid black;"><td style="background-color:{colors[0]}">&nbsp&nbsp&nbsp&nbsp</td></tr>
    <tr style="border: 1px solid black;"><td style="background-color:{colors[1]}">&nbsp&nbsp&nbsp&nbsp</td></tr>
    <tr style="border: 1px solid black;"><td style="background-color:{colors[2]}">&nbsp&nbsp&nbsp&nbsp</td></tr>
    </table>
    """

def level(idx,seq,level,beaker):
    return f"""<select name="i{idx}_s{seq}_b{beaker}_l{level}" onchange="this.style='background:'+this.value;">
    <option value="white" selected>Empty</option>
    <option value="green">Green</option>
    <option value="orange">Orange</option>
    <option value="purple">Purple</option>
    <option value="yellow">Yellow</option>
    <option value="red">Red</option>
    <option value="brown">Brown</option>
    </select>
    <br />
    """
def recipe_page(idx):
    df_sc1 = df.query(f"id=='dev-{idx}'")
    html="""
    <table>
        <tr>
        <th>Instruction</th>
        <th>1</th>
        <th>2</th>
        <th>3</th>
        <th>4</th>
        <th>5</th>
        <th>6</th>
        <th>7</th>
        </tr>
    """
    for i,row in df_sc1.iterrows():
        if row["seq"]==0:
            html+=f"""<tr>
            <td>Initial State</td>
            <td>{block(row,1)}</td>
            <td>{block(row,2)}</td>
            <td>{block(row,3)}</td>
            <td>{block(row,4)}</td>
            <td>{block(row,5)}</td>
            <td>{block(row,6)}</td>
            <td>{block(row,7)}</td>
            </tr>
        """
            continue
        html+=f"""<tr>
            <td>{row["instruction"]}</td>
            <td>{level(idx,row["seq"],3,1)}{level(idx,row["seq"],2,1)}{level(idx,row["seq"],1,1)}</td>
            <td>{level(idx,row["seq"],3,2)}{level(idx,row["seq"],2,2)}{level(idx,row["seq"],1,2)}</td>
            <td>{level(idx,row["seq"],3,3)}{level(idx,row["seq"],2,3)}{level(idx,row["seq"],1,3)}</td>
            <td>{level(idx,row["seq"],3,4)}{level(idx,row["seq"],2,4)}{level(idx,row["seq"],1,4)}</td>
            <td>{level(idx,row["seq"],3,5)}{level(idx,row["seq"],2,5)}{level(idx,row["seq"],1,5)}</td>
            <td>{level(idx,row["seq"],3,6)}{level(idx,row["seq"],2,6)}{level(idx,row["seq"],1,6)}</td>
            <td>{level(idx,row["seq"],3,7)}{level(idx,row["seq"],2,7)}{level(idx,row["seq"],1,7)}</td>
            </tr>
        """
    html+="</table>"
    return html



html="""
<html><head>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<style>
select option[value="red"] { background: red;}
select option[value="green"] {background: green;}
select option[value="brown"] {background: brown;}
select option[value="orange"] {background: orange;}
select option[value="white"] {background: white;}
select option[value="purple"] {background: purple;}
select option[value="yellow"] {background: yellow;}
</style>
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
</head>
<body>
<div id="content"><div class="row"><div class="col-sm-1"></div><div class="col-sm-10">
<FORM method="POST" id="mturk_form" name="mturk_form">
        <div class="row">
            <div class="col-sm-1"><h1 class="glyphicon glyphicon-backward" id="prev_instruction" onclick="prev_instruction();"></h1></div>
            <div class="col-sm-10" id="instruction"><h3>1/7</h3></div>
            <div class="col-sm-1"><h1 class="glyphicon glyphicon-forward" id="next_instruction" onclick="next_instruction();"></h1></div>
        </div>
        <div class="row" id="page_0">
        <h1>Welcome</h1>
        In this task you will be shown 5 protocols, in each of them you will be asked to pour liquid from one beaker to another.<br />
        You will be asked to annotate the color of the liquid you poured into the beaker and the amount of units.<br />
        The first row will be the initial state of the beakers<br />
        At the end of the 5 protocols, you will be asked a few questions to describe your expirience<br />
        </div>
"""
#page 1
html+="""<div class="row" id="page_1" style="display:none">""" + recipe_page(1831) + "</div>"
#page 2
html+="""<div class="row" id="page_2" style="display:none">""" + recipe_page(1834) + "</div>"
#page 3
html+="""<div class="row" id="page_3" style="display:none">""" + recipe_page(1835) + "</div>"
#page 4
html+="""<div class="row" id="page_4" style="display:none">""" + recipe_page(1836) + "</div>"
#page 5
html+="""<div class="row" id="page_5" style="display:none">""" + recipe_page(1837) + "</div>"


html+="""
        <div class="row" id="page_6" style="display:none">
        <h1>A few questions</h1>
        </div>
    <script>

        let instruction_index=0;
        const instructions_length=7;//TODO: get this from the database
        function getUrlParam(name) {
        var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : null;
        }
        function save()
        {
            const form = document.getElementById("mturk_form");
            const turk_submit = getUrlParam('turkSubmitTo');
            if (turk_submit) {
                form.action=turk_submit + '/mturk/externalSubmit';
                document.getElementById("assignmentId").value = getUrlParam('assignmentId');
            }
            form.submit();
        }
        function hide_all_pages() {
            for (let i=0;i<instructions_length;i++)
            {
                document.getElementById("page_"+i).style.display="none";
            }
        }
        function next_instruction()
        {
            console.log("next_instruction");
            if (instruction_index+1==instructions_length){
                if (!confirm("You are about to submit the annotations,\\n\\nEMPTY ANNOTATIONS WILL BE REJECTED \\n\\n are you sure ?"))
                    return;
                save();
                return;
            }
            instruction_index+=1;
            hide_all_pages();
            document.getElementById("instruction").innerHTML="<h3>"+instruction_index+"/"+instructions_length+"</h3>";
            document.getElementById("page_"+instruction_index).style.display="block";
        }
        function prev_instruction()
        {
            console.log("prev_instruction");
            if (instruction_index==0)
                return;
            instruction_index-=1;
            hide_all_pages();
            document.getElementById("instruction").innerHTML="<h3>"+instruction_index+"/"+instructions_length+"</h3>";
            document.getElementById("page_"+instruction_index).style.display="block";
        }

        // main ()
        document.addEventListener("DOMContentLoaded", function(event) {

              //Ignore the enter key, as it seem to submit the HIT for some turkers
              $(document).on("keydown", "form", event=>event.key != "Enter");
            const submitButton = document.getElementById("submitButton");
            if (submitButton){
              submitButton.style.display = "none";
            }
        });
        </script>
</FORM></div>
<div class="col-sm-1"></div>
</div></div></body></html>"""


with output_file.open('w') as f:
    f.write(html)

# %%