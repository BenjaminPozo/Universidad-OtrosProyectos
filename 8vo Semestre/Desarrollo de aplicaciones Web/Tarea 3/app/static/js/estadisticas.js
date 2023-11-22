document.addEventListener('DOMContentLoaded', function () {
  fetch('/obtener_datos_hincha')
      .then(response => response.json())
      .then(datos => {
          var etiquetas = datos.map(item => item.deporte);
          var valores = datos.map(item => item.count);

          var ctx = document.getElementById('graficoHinchas').getContext('2d');
          var myChart = new Chart(ctx, {
              type: 'bar',  
              data: {
                  labels: etiquetas,
                  datasets: [{
                      label: 'Cantidad Hinchas',
                      data: valores,
                      backgroundColor: '#494d5f',
                      borderColor: 'pink',
                      borderWidth: 1
                  }]
              }
          });
      })
      .catch(error => console.error('Error en la solicitud AJAX:', error));
});

document.addEventListener('DOMContentLoaded', function () {
  fetch('/obtener_datos_artesano')
      .then(response => response.json())
      .then(datos => {
          var etiquetas = datos.map(item => item.tipo);
          var valores = datos.map(item => item.count);

          var ctx = document.getElementById('graficoArtesanos').getContext('2d');
          var myChart = new Chart(ctx, {
              type: 'bar',  
              data: {
                  labels: etiquetas,
                  datasets: [{
                      label: 'Cantidad Artesanos',
                      data: valores,
                      backgroundColor: '#494d5f',
                      borderColor: 'pink',
                      borderWidth: 1
                  }]
              }
          });
      })
      .catch(error => console.error('Error en la solicitud AJAX:', error));
});
