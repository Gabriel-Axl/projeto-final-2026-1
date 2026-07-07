const fields = [

["gender","select",["Female","Male"]],
["SeniorCitizen","number"],
["Partner","select",["Yes","No"]],
["Dependents","select",["Yes","No"]],
["tenure","number"],
["PhoneService","select",["Yes","No"]],
["MultipleLines","select",["Yes","No","No phone service"]],
["InternetService","select",["DSL","Fiber optic","No"]],
["OnlineSecurity","select",["Yes","No","No internet service"]],
["OnlineBackup","select",["Yes","No","No internet service"]],
["DeviceProtection","select",["Yes","No","No internet service"]],
["TechSupport","select",["Yes","No","No internet service"]],
["StreamingTV","select",["Yes","No","No internet service"]],
["StreamingMovies","select",["Yes","No","No internet service"]],
["Contract","select",["Month-to-month","One year","Two year"]],
["PaperlessBilling","select",["Yes","No"]],
["PaymentMethod","select",[
"Electronic check",
"Mailed check",
"Bank transfer (automatic)",
"Credit card (automatic)"
]],
["MonthlyCharges","number"],
["TotalCharges","number"]

];

const form=document.getElementById("predictForm");

fields.forEach(field=>{

    let label=document.createElement("label");

    label.innerText=field[0];

    form.appendChild(label);

    if(field[1]=="number"){

        let input=document.createElement("input");

        input.type="number";

        input.id=field[0];

        input.step="any";

        form.appendChild(input);

    }

    else{

        let select=document.createElement("select");

        select.id=field[0];

        field[2].forEach(option=>{

            let o=document.createElement("option");

            o.value=option;

            o.innerHTML=option;

            select.appendChild(o);

        });

        form.appendChild(select);

    }

});


async function predict(){

    const body={};

    fields.forEach(field=>{

        const value=document.getElementById(field[0]).value;

        body[field[0]]=field[1]=="number" ? Number(value) : value;

    });

    const response=await fetch("http://localhost:8000/predict",{

        method:"POST",

        headers:{

            "Content-Type":"application/json"

        },

        body:JSON.stringify(body)

    });

    const result=await response.json();

    document.getElementById("result").innerHTML=`

<h2>Resultado</h2>

<p><b>Probabilidade:</b> ${Math.round(result.probabilidade*100)}%</p>

<p><b>Classificação:</b> ${result.classificacao}</p>

<p><b>Explicação:</b><br>${result.explicacao}</p>

<p><b>Ação sugerida:</b><br>${result.acao_sugerida}</p>

`;

}