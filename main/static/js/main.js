function getCookie(name) {
    let cookieValue = null;
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
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
function invitePlayer(playerId) {     console.log("Inviting player with id:", playerId)
    const csrftoken = getCookie('csrftoken');
    console.log("CSRF Token: " + csrftoken);
    const url = '/game/invite/';
    console.log("Sending invite to: " + url);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            },
        body: JSON.stringify({'player_id': playerId}),
        })
        .then((response) => {
            console.log("Response: " + response);
            if (response.ok) {
                return response.json();
                }
            else {
                    throw new Error('Ошибка сервера');
                }
            })
            .then((data) => {
                console.log("Data: " + JSON.stringify(data));
                if (!data.error) {
                    window.location.href = '/game/board/' + data.game_id + '/';
                } else {
                    throw new Error(data.error);
                }
            })
            .catch((error) => {
                console.error('Ошибка:', error);
            });
}
