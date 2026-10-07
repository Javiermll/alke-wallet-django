/* ============================================================
   Alke Wallet: comportamientos pequeños del navegador
   Todo funciona sin este archivo; solo mejora la experiencia.
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    /* 1. Ver u ocultar la contraseña ------------------------------------
       A cada campo de contraseña se le agrega un botón con un ojo.
       Al pulsarlo, el campo cambia entre type="password" y type="text". */
    document.querySelectorAll('input[type="password"]').forEach(function (campo) {
        // Se envuelve el campo en un grupo de Bootstrap para poner el botón a su derecha
        var grupo = document.createElement('div');
        grupo.className = 'input-group';
        campo.parentNode.insertBefore(grupo, campo);
        grupo.appendChild(campo);

        var boton = document.createElement('button');
        boton.type = 'button';
        boton.className = 'btn btn-outline-secondary';
        boton.setAttribute('aria-label', 'Mostrar u ocultar la contraseña');
        boton.innerHTML = '<i class="bi bi-eye"></i>';
        grupo.appendChild(boton);

        boton.addEventListener('click', function () {
            var visible = campo.type === 'text';
            campo.type = visible ? 'password' : 'text';
            boton.innerHTML = visible ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
        });
    });

    /* 2. Evitar el doble envío de los formularios -----------------------
       Al enviar un formulario POST, el botón se desactiva y muestra un
       indicador de carga. Así un doble clic no registra dos veces el
       mismo movimiento. Los filtros (GET) no se tocan. */
    document.querySelectorAll('form[method="post"]').forEach(function (formulario) {
        formulario.addEventListener('submit', function () {
            var boton = formulario.querySelector('button[type="submit"]');
            // El botón de cerrar sesión del menú no necesita indicador
            if (!boton || boton.classList.contains('dropdown-item')) { return; }
            // Se espera un instante: desactivar el botón antes de enviar podría cancelar el envío
            setTimeout(function () {
                boton.disabled = true;
                boton.insertAdjacentHTML('afterbegin', '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>');
            }, 0);
        });
    });

    // Si se vuelve a esta página con el botón Atrás, los botones deben quedar activos otra vez
    window.addEventListener('pageshow', function (evento) {
        if (!evento.persisted) { return; }
        document.querySelectorAll('form[method="post"] button[type="submit"]').forEach(function (boton) {
            boton.disabled = false;
            var indicador = boton.querySelector('.spinner-border');
            if (indicador) { indicador.remove(); }
        });
    });

    /* 3. Cerrar solos los avisos de éxito --------------------------------
       Los avisos verdes desaparecen a los 6 segundos; los de error y
       advertencia se quedan hasta que la persona los cierre. */
    document.querySelectorAll('.alert-success.alert-dismissible').forEach(function (aviso) {
        setTimeout(function () {
            if (window.bootstrap && document.body.contains(aviso)) {
                bootstrap.Alert.getOrCreateInstance(aviso).close();
            }
        }, 6000);
    });
});
