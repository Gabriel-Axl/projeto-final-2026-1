const fields = [


["gender","select",[["Female","Feminino"],["Male","Masculino"]], "Gênero", "Sexo do cliente."],
["SeniorCitizen","number", null, "Idoso (SeniorCitizen)", "Indicador se o cliente é senior (1) ou não (0)."],
["Partner","select",[["Yes","Sim"],["No","Não"]], "Parceiro", "Cliente tem parceiro? (Sim/Não)."],
["Dependents","select",[["Yes","Sim"],["No","Não"]], "Dependentes", "Cliente possui dependentes? (Sim/Não)."],
["tenure","number", null, "Tempo de contrato (meses)", "Meses desde o início do contrato com a empresa."],
["PhoneService","select",[["Yes","Sim"],["No","Não"]], "Serviço de telefone", "O cliente possui serviço de telefone?"],
["MultipleLines","select",[["Yes","Sim"],["No","Não"],["No phone service","Sem serviço de telefone"]], "Linhas múltiplas", "Se o cliente tem múltiplas linhas de telefone."],
["InternetService","select",[["DSL","DSL"],["Fiber optic","Fibra ótica"],["No","Sem internet"]], "Serviço de Internet", "Tipo de conexão de internet do cliente."],
["OnlineSecurity","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Segurança online", "Serviço de segurança online ativo?"],
["OnlineBackup","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Backup online", "Serviço de backup na nuvem ativo?"],
["DeviceProtection","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Proteção do dispositivo", "Proteção contra danos/roubo do dispositivo?"],
["TechSupport","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Suporte técnico", "Acesso a suporte técnico 24/7?"],
["StreamingTV","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Streaming TV", "O cliente usa serviço de streaming de TV?"],
["StreamingMovies","select",[["Yes","Sim"],["No","Não"],["No internet service","Sem internet"]], "Streaming Filmes", "O cliente usa serviço de streaming de filmes?"],
["Contract","select",[["Month-to-month","Mês a mês"],["One year","Um ano"],["Two year","Dois anos"]], "Contrato", "Tipo de contrato (mês a mês, 1 ano, 2 anos)."],
["PaperlessBilling","select",[["Yes","Sim"],["No","Não"]], "Faturamento sem papel", "Cliente usa faturamento eletrônico?"],
["PaymentMethod","select",[["Electronic check","Cheque eletrônico"],["Mailed check","Cheque enviado"],["Bank transfer (automatic)","Transferência bancária (automática)"],["Credit card (automatic)","Cartão de crédito (automático)"]], "Método de pagamento", "Forma de pagamento utilizada pelo cliente."],
["MonthlyCharges","number", null, "Cobrança mensal", "Valor cobrado por mês ao cliente."],
["TotalCharges","number", null, "Cobrança total", "Total cobrado ao cliente desde o início do contrato."]

];

const form=document.getElementById("predictForm");

// auth state
let accessToken = null;
let cachedApiKey = null;

document.getElementById("loginBtn").addEventListener("click", async (e)=>{
    e.preventDefault();
    await doLogin();
});

function showMessage(msg){
    const el = document.getElementById("loginMsg");
    if(el) el.innerText = msg;
}

async function doLogin(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try{
        const res = await fetch('/login',{
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({username, password})
        });

        if(!res.ok){
            const err = await res.json();
            showMessage(err.detail || 'Login falhou');
            return;
        }

        const data = await res.json();
        accessToken = data.access_token;
        localStorage.setItem('access_token', accessToken);

        // fetch API key
        await fetchApiKey();

        // show app
        document.getElementById('loginArea').style.display = 'none';
        document.getElementById('appArea').style.display = 'block';
        showMessage('');

    }catch(err){
        showMessage('Erro ao conectar: '+err.message);
    }
}

async function fetchApiKey(){
    if(!accessToken) accessToken = localStorage.getItem('access_token');
    const res = await fetch('/get_api_key',{
        headers: {'Authorization': 'Bearer '+accessToken }
    });
    if(!res.ok) throw new Error('Não autorizado para obter API key');
    const d = await res.json();
    cachedApiKey = d.api_key;
}

function logout(){
    accessToken = null;
    cachedApiKey = null;
    localStorage.removeItem('access_token');
    document.getElementById('loginArea').style.display = 'block';
    document.getElementById('appArea').style.display = 'none';
}

fields.forEach(field=>{

    let label=document.createElement("label");
    label.innerText=field[3] || field[0];
    form.appendChild(label);

    // description below the label
    if(field[4]){
        let desc = document.createElement("div");
        desc.className = "field-desc";
        desc.innerText = field[4];
        form.appendChild(desc);
    }

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

        (field[2]||[]).forEach(opt=>{
            let val, label;
            if(Array.isArray(opt)){
                val = opt[0];
                label = opt[1];
            } else {
                val = opt;
                label = opt;
            }

            let o=document.createElement("option");
            o.value = val;
            o.innerText = label;
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

    // ensure we have API key
    if(!cachedApiKey){
        // try to refresh
        await fetchApiKey();
    }

    const response=await fetch("/predict",{

        method:"POST",

        headers:{
            "Content-Type":"application/json",
            "X-API-Key": cachedApiKey
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