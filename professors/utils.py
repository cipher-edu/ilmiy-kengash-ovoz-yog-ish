# apps/utils.py

def get_csrf_token_js():
    """
    Shablonlarga qo'shish uchun CSRF tokenini olish va AJAX so'rovlariga sozlash uchun JavaScript kodi.
    """
    return """
    <script>
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        // jQuery AJAX sozlamalari (agar ishlatilsa)
        if (typeof jQuery !== 'undefined') {
            jQuery.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }
        
        // Fetch API uchun sozlama
        // const headers = {
        //     'Content-Type': 'application/json',
        //     'X-CSRFToken': csrftoken
        // };
        // fetch(url, { method: 'POST', headers: headers, body: ... });
    </script>
    """