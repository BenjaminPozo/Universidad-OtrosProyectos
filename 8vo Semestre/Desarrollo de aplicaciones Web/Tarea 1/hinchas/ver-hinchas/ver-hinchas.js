const lcls = localStorage.getItem("hinchas");
const jsonHinchas = JSON.parse(lcls);

let listaHinchas = document.getElementById("listaHinchas")
jsonHinchas.hinchas.forEach((json, indice) => {
  const tr = document.createElement('tr');
  const deportesLista = json.deportes;
  let deportes = '';
  deportesLista.forEach(dep => {
    deportes += dep + ', ';
  })
  deportes = deportes.slice(0, -2)
  const comuna = json.comuna;
  const transporte = json.transporte;
  const nombre = json.nombre;
  const celular = json.celular;
  const atr = [nombre, comuna, deportes, transporte, celular];
  atr.forEach(elemento => { 
    const td = document.createElement('td');
    if (elemento === '') {
      td.textContent = 'No hay datos';
      td.style.color = 'red'
    } else {
      td.textContent = elemento;
    }
    tr.appendChild(td);
  })
  const button = document.createElement('button');
  button.textContent = 'Ver más'; 
  button.className = 'ver-mas-button';
  button.addEventListener('click', () => {
    localStorage.setItem('hinchaIndex', indice);
    window.location.href = '../informacion-hincha/informacion-hincha.html';
  });
  tr.appendChild(button),
  listaHinchas.appendChild(tr)
});

