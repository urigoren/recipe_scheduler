import collections, itertools, json, re, operator
from functools import reduce
from pathlib import Path
import pandas as pd

data_dir = Path(__file__).absolute().parent.parent /"data"/"scone"

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
color2name = {
            "w":"white",
            "r":"red",
            "b":"brown",
            "y":"yellow",
            "p":"purple",
            "o":"orange",
            "g":"green",
        }


def block(row, beaker=0):
    if beaker>0:
        ccc = ("www"+row[beaker].replace("_",""))[-3:]
    else:
        ccc = ("www"+row.replace("_",""))[-3:]
    colors = {}
    for i,c in enumerate(ccc):
        colors[i]=color2name[c]
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
def beaker_page(idx):
    df_sc1 = df.query(f"id=='dev-{idx}'")
    html="""
    <table border="2">
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

def code_page(idx):
    df_sc1 = df.query(f"id=='dev-{idx}'")
    html="""
    <table border="2">
        <tr>
        <th>Instruction</th>
        <th>Command</th>
        <th>Arg 1</th>
        <th>Arg 2</th>
        <th>Arg 3</th>
        </tr>
    """
    for i,row in df_sc1.iterrows():
        if row["seq"]==0:
            beakers = [{"r":0,"b":0,"y":0,"p":0,"o":0,"g":0} for _ in range(7)]
            for beaker_index in range(1,8):
                for c in row[beaker_index]:
                    if c=="_":
                        continue
                    beakers[beaker_index-1][c]+=1
            for beaker_index in range(7):
                for c in "rbygpo":
                    if beakers[beaker_index][c]==0:
                        continue
                    html+=f"""<tr>
                    <td>&nbsp;</td>
                    <td>PUT</td>
                    <td>{beakers[beaker_index][c]} Unit</td>
                    <td>{color2name[c]}</td>
                    <td>Beaker {beaker_index+1}</td>
                    </tr>
                """
            continue
        html+=f"""<tr>
            <td>{row["instruction"]}</td>
            <td><select name="i{idx}_s{row["seq"]}_cmd"><option value="NONE" selected></option><option value="MOVE">Move</option><option value="REM">Remove</option><option value="MIX">Mix</option></select></td>
            <td><select name="i{idx}_s{row["seq"]}_arg1"><option value="" selected></option><option value="1">Beaker 1</option><option value="2">Beaker 2</option><option value="3">Beaker 3</option><option value="4">Beaker 4</option><option value="5">Beaker 5</option><option value="6">Beaker 6</option><option value="7">Beaker 7</option></select></td>
            <td><select name="i{idx}_s{row["seq"]}_arg2"><option value="" selected></option><option value="1">Beaker 1</option><option value="2">Beaker 2</option><option value="3">Beaker 3</option><option value="4">Beaker 4</option><option value="5">Beaker 5</option><option value="6">Beaker 6</option><option value="7">Beaker 7</option></select></td>
            <td><select name="i{idx}_s{row["seq"]}_arg3"><option value="" selected></option><option value="1">1 Unit</option><option value="2">2 Units</option><option value="3">3 Units</option></select></td>
            </tr>
        """
    html+="</table>"
    return html


def anootation_html(recipes=[1831,1834,1835,1836,1837],code=False):
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
    <input type="hidden" name="seconds_spent" id="frm_seconds_spent" value="[]">
            <div class="row">
                <div class="col-sm-1"><h1 class="glyphicon glyphicon-backward" id="prev_instruction" onclick="prev_instruction();"></h1></div>
                <div class="col-sm-10" id="instruction"><h3>0/6</h3></div>
                <div class="col-sm-1"><h1 class="glyphicon glyphicon-forward" id="next_instruction" onclick="next_instruction();"></h1></div>
            </div>
    """
    if code:
        html+=f"""
<div id="page_0" class="row">
<h1>Welcome</h1>
<p>In this task, your role will be to translate 5 short scientific procedures into code and to answer a questionnaire regarding how was the task for you.&nbsp;</p>
<p>In each scientific procedure, there are 7 beakers with liquids in them, and you will get the initial state of the beakers written in code using the PUT command.&nbsp;</p>
<p>The <strong>PUT</strong> command gets 3 arguments: <strong>the beaker</strong> we put liquids to (where B1 refers to 1st beaker and B7 refers to the 7th beaker), <strong>the color</strong> of the liquid we want to put in that beaker, and the number of <strong>units</strong> <strong>of liquid</strong>&nbsp;we put in that beaker.&nbsp;</p>
<p>For example,&nbsp;</p>
<img src="http://goren.ml/cdn/beakernum.png" width="426" height="104" />
<div class="row">The code for the initial state of the beakers above will be given to you in code as follows:&nbsp;</div>
<div class="row">&nbsp;</div>
<div class="row">PUT B1 green 2 (= put in the 1st beaker 2 units of green liquid)</div>
<div class="row">PUT B2 red 1</div>
<div class="row">PUT B3 green 1</div>
<div class="row">PUT B5 orange 1</div>
<div class="row">PUT B6 yellow 2</div>
<div class="row">PUT B7 orange 1</div>
<div class="row">&nbsp;</div>
<div class="row">After getting the initial state of the beakers, you will get a sequence of instructions that will be executed one after another. In these instructions, you will be asked to <span style="text-decoration: underline;"><strong>REMOVE</strong></span>&nbsp;liquids from a specific beaker, <strong><u>MOVE </u></strong>liquids from one beaker to another, or <strong><u>MIX</u> </strong>liquids in a specific beaker. Your role will be to translate these instructions into code.</div>
<div class="row">&nbsp;</div>
<div class="row">For translating the instructions into code, you can use the following three commands:</div>
<ul>
<li>The <span style="text-decoration: underline;"><strong>REMOVE</strong></span> command gets 2 arguments: <strong>the beaker</strong> from which we remove content, and the number of<strong> units of liquid</strong> to remove.</li>
</ul>
<p style="padding-left: 40px;">For example, given the initial state above, the instruction <strong>"throw out the yellow chemical"</strong> should be translated into&nbsp;<strong>"REMOVE B6 2" </strong>(as only the 6th beaker has a yellow chemical and it has two units of that chemical). After executing that command, the new state will look like that:&nbsp;</p>
<p style="padding-left: 40px;"><img src="http://goren.ml/cdn/beakers_exp_remove.png" width="426" height="104" /></p>
<ul>
<li class="row">The <span style="text-decoration: underline;"><strong>MOVE</strong></span> command gets 3 arguments: <strong>the beaker</strong> from which we take the content, <strong>the beaker</strong> we move the content into, and the number of <strong>units of liquid</strong> to move.</li>
</ul>
<p style="padding-left: 40px;">For example, <strong>"pour the third beaker into the fifth one"</strong> should be translated into <strong>"MOVE B3 B5 1"</strong>, and the new state will look like that:</p>
<p style="padding-left: 40px;"><img src="http://goren.ml/cdn/beakers_exp_move.png" width="426" height="104" /></p>
<ul>
<li class="row">The <span style="text-decoration: underline;"><strong>MIX</strong></span> command gets just one argument - <strong>the beaker</strong> to be mixed. <span style="color: #ff0000;"><strong>NOTE THAT</strong></span> mixing two different colors in a beaker turns the color of the liquid in that beaker into <span style="color: #993300;"><strong>brown</strong></span>.&nbsp;</li>
</ul>
<p style="padding-left: 40px;">For example,&nbsp;<strong>"mix the fifth beaker"</strong> should be translated into&nbsp;<strong>"MIX B5"</strong>, and the new state will look like that:</p>
<p style="padding-left: 40px;"><img src="http://goren.ml/cdn/beakers_exp_mix.png" width="426" height="104" /></p>
            </div>
        """
        for i, rid in enumerate(recipes):
            html+=f"""<div class="row" id="page_{i+1}" style="display:none">{code_page(rid)}</div>""" 
    else:
        html+=f"""
            <div class="row" id="page_0">
            <h1>Welcome</h1>
            <img src="http://goren.ml/cdn/beakernum.png"/><br />
            In this task you will be shown 5 protocols, in each of them you will be asked to pour liquid from one beaker to another.<br />
            You will be asked to annotate the color of the liquid you poured into the beaker and the amount of units.<br />
            The first row will be the initial state of the beakers<br />
            At the end of the 5 protocols, you will be asked a few questions to describe your expirience<br />
            <h2>Example annotation</h2>
            <table border="2">
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
            <tr>
            <td>Initial State</td>
            <td style="padding-left:20px;padding-right:20px;">{block("y")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("rrr")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("pp")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("g")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("yg")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("b")}</td>
            </tr>
            <tr>
            <td>Pour 2 units of red color from beaker 2 to beaker 4</td>
            <td style="padding-left:20px;padding-right:20px;">{block("y")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("r")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("pp")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("rrg")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("yg")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("")}</td>
            <td style="padding-left:20px;padding-right:20px;">{block("b")}</td>
            </tr>
            </table>
            </div>
        """
        for i, rid in enumerate(recipes):
            html+=f"""<div class="row" id="page_{i+1}" style="display:none">{beaker_page(rid)}</div>""" 

    html+="""
            <div class="row" id="page_6" style="display:none">
            <h1>A few questions</h1>
            (1)   Describe what did you like and dislike while performing the task? (open question, mandatory)<br />
            <textarea name="q1"></textarea><br/>

    (2)   Rate how easy was the task for you? (1 – not easy at all, 5 – very easy)<br />
    <select name="q2"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (3)   Rate how clear was the task for you? (1 – not clear at all, 5 – very clear)<br />
    <select name="q3"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (4)   Rate how intuitive was the task for you? (1 – not intuitive at all, 5 – very intuitive)<br />
    <select name="q4"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>
    

    (5)   How satisfied are you with the quality of your annotations? (1 – not satisfied at all, 5 – very satisfied)<br />
    <select name="q5"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    

    (6)   How comfortable did you feel while performing the task? (1 – not comfortable at all, 5 – very comfortable)<br />
    <select name="q6"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (7)   How confident did you feel while performing the task? (1 – not confident at all, 5 – very confident)<br />
    <select name="q7"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (8)   How confused did you feel when performing the task? (1 – not confused at all, 5 – very confused)<br />
    <select name="q8"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (9)   How frustrated did you feel when performing the task? (1 – not frustrated at all, 5 – very frustrated)<br />
    <select name="q9"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    
    (10)Do you have any suggestions for improving the task? (open question, optional)<br />
    <textarea name="q10"></textarea><br/>
    

    (11)Rate how clear was the user interface for you? (1 – not clear at all, 5 – very clear)<br />
    <select name="q11"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    (12)Rate how intuitive was the user interface for you? (1 – not intuitive at all, 5 – very intuitive)<br />
    <select name="q12"><option value="" selected>Please rate</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select><br/>

    
    (13)Do you have any suggestions for improving the user interface? (open question, optional)<br />
    <textarea name="q13"></textarea><br/>
    

    (14)Any other comments? (open question, optional)<br />
    <textarea name="q14"></textarea><br/>
            </div>
        <script>

            let instruction_index=0;
            const instructions_length=7;//TODO: get this from the database
            let seconds_spent=[0,0,0,0,0,0,0];
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
                document.getElementById('frm_seconds_spent').value=JSON.stringify(seconds_spent);
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
                document.getElementById("instruction").innerHTML="<h3>"+instruction_index+"/"+(instructions_length-1)+"</h3>";
                document.getElementById("page_"+instruction_index).style.display="block";
            }
            function prev_instruction()
            {
                console.log("prev_instruction");
                if (instruction_index==0)
                    return;
                instruction_index-=1;
                hide_all_pages();
                document.getElementById("instruction").innerHTML="<h3>"+instruction_index+"/"+(instructions_length-1)+"</h3>";
                document.getElementById("page_"+instruction_index).style.display="block";
            }

            // main ()
            document.addEventListener("DOMContentLoaded", function(event) {

                setInterval(()=>{seconds_spent[instruction_index]+=1;},1000);


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
    return html


if __name__=="__main__":
    output_dir = Path(__file__).absolute().parent.parent /"mturk"
    with (output_dir/"scone_code_mturk.html").open('w') as f:
        f.write(anootation_html(code=True))
    with (output_dir/"scone_scheduler_mturk.html").open('w') as f:
        f.write(anootation_html(code=False))

# %%
