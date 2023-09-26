const lcls = localStorage.getItem("artesanos");
const jsonArtesanos = JSON.parse(lcls);
let listaArtesanos = document.getElementById("listaArtesanos")

jsonArtesanos.artesanos.forEach((json, indice) => {

  const tr = document.createElement('tr');
  const tiposLista = json.tipos;
  let tipos = '';
  tiposLista.forEach(tipo => {
    tipos += tipo + ', ';
  })
  tipos = tipos.slice(0, -2);
  const comuna = json.comuna;
  const nombre = json.nombre;
  const celular = json.celular;
  const atr = [nombre, celular, comuna, tipos];

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
  listaArtesanos.appendChild(tr)

  const fotos = json.fotos;
  const td = document.createElement('td');
  for (let i = 0; i < fotos.length; i++) {
    const img = document.createElement('img');
    img.src = fotos[i];
    img.width = '120px';
    td.appendChild(img);
  }
  
  tr.appendChild(td);

  const button = document.createElement('button');
  button.textContent = 'Ver más'; 
  button.className = 'ver-mas-button';
  button.addEventListener('click', () => {
    localStorage.setItem('artesanoIndex', indice);
    window.location.href = '../informacion-artesano/informacion-artesano.html';
  });
  tr.appendChild(button),
  listaArtesanos.appendChild(tr)
});

