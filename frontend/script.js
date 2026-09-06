const API_URL = "http://localhost:8000"; // En ZimaOS cámbialo si es necesario
let TOKEN = "";

// --- LOGIN ---
async function login() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    
    try {
        const res = await fetch(`${API_URL}/login?username=${user}&password=${pass}`, { method: 'POST' });
        const data = await res.json();
        if (data.token) {
            TOKEN = data.token;
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
            loadInventory();
        } else { alert("Login fallido"); }
    } catch (e) { alert("Error conectando al servidor"); }
}

function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById(id).classList.remove('hidden');
    if(id === 'inventario') loadInventory();
    if(id === 'montar') loadStockForAssembly();
    if(id === 'ventas') loadPCs();
}

// --- BUSCADOR INTERNET (WIKIPEDIA) ---
async function buscarInternet(query) {
    if (query.length < 3) { document.getElementById('sugerencias').classList.add('hidden'); return; }
    
    const res = await fetch(`https://es.wikipedia.org/w/api.php?action=opensearch&search=${query}&limit=5&namespace=0&format=json&origin=*`);
    const data = await res.json();
    
    const sugBox = document.getElementById('sugerencias');
    sugBox.innerHTML = "";
    sugBox.classList.remove('hidden');
    
    data[1].forEach(item => {
        const div = document.createElement('div');
        div.innerText = item;
        div.onclick = () => {
            document.getElementById('comp-name').value = item;
            sugBox.classList.add('hidden');
        };
        sugBox.appendChild(div);
    });
}

// --- LOGICA DE INVENTARIO ---
async function addBulk() {
    const name = document.getElementById('comp-name').value;
    const cat = document.getElementById('comp-cat').value;
    const qty = document.getElementById('comp-qty').value;
    const price = document.getElementById('comp-price').value;

    await fetch(`${API_URL}/components/add-bulk?name=${name}&category=${cat}&quantity=${qty}&price_per_unit=${price}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${TOKEN}` }
    });
    loadInventory();
    alert("Añadido");
}

async function addBundle() {
    const names = document.getElementById('bundle-names').value.split(',').map(n => n.trim());
    const total = document.getElementById('bundle-total-price').value;

    await fetch(`${API_URL}/components/add-bundle?total_price=${total}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${TOKEN}` },
        body: JSON.stringify(names)
    });
    loadInventory();
    alert("Bundle dividido y añadido");
}

async function loadInventory() {
    const res = await fetch(`${API_URL}/components/available`, { headers: { 'Authorization': `Bearer ${TOKEN}` }});
    const items = await res.json();
    const tabla = document.getElementById('tabla-stock');
    tabla.innerHTML = items.map(i => `<tr class="border-b"><td>${i.id}</td><td>${i.name}</td><td>${i.purchase_price}€</td><td>${i.category}</td></tr>`).join('');
}

// --- LOGICA DE MONTAJE ---
async function loadStockForAssembly() {
    const res = await fetch(`${API_URL}/components/available`, { headers: { 'Authorization': `Bearer ${TOKEN}` }});
    const items = await res.json();
    const div = document.getElementById('lista-seleccion-componentes');
    div.innerHTML = items.map(i => `
        <label class="block p-2 border rounded cursor-pointer hover:bg-blue-50">
            <input type="checkbox" value="${i.id}" class="comp-checkbox"> ${i.name} (${i.purchase_price}€)
        </label>
    `).join('');
}

async function assemblePC() {
    const name = document.getElementById('pc-name').value;
    const selected = Array.from(document.querySelectorAll('.comp-checkbox:checked')).map(cb => parseInt(cb.value));
    
    await fetch(`${API_URL}/pc/assemble?pc_name=${name}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${TOKEN}` },
        body: JSON.stringify(selected)
    });
    alert("PC Registrado");
    showSection('ventas');
}

async function loadPCs() {
    // Aquí llamaríamos a un endpoint de PCs (debes tenerlo en el backend para listar)
    // Por brevedad, este fetch asume que el backend tiene GET /pcs
    const res = await fetch(`${API_URL}/pcs-all`, { headers: { 'Authorization': `Bearer ${TOKEN}` }}); 
    // Nota: Deberías añadir este endpoint GET /pcs-all en main.py para ver la lista completa
}