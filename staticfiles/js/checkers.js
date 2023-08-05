document.addEventListener('DOMContentLoaded', function () {
    let game_id = getGameIdFromUrl()
    var socket = new WebSocket(`ws://${window.location.host}/game/board/${game_id}/`);
    const cells = document.querySelectorAll('.cell');
    let selectedCheckerId = null;

    socket.onopen = function (e) {
        console.log("[open] Connection established");
    };

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const message = data['message'];
        const capture = data['capture'];
        const attacking_checker = data['attacking_checker'];
        const captured_checkers = data['captured_checkers'];
        const can_continue_attack = data['can_continue_attack'];

        console.log("[message] Data received from server: ", data);

        if (message === 'Успешный ход' || message === 'Успешная атака') {
            const cell = document.querySelector(`[data-row-index="${data.new_row}"][data-cell-number="${data.new_column}"]`);
            handleMoveOrAttackSuccess.call(cell);
            if (message === 'Успешная атака') {
                // Remove the captured checker from the board
                captured_checkers.forEach(checkerId => {
                    let capturedChecker = document.querySelector(`[data-checker-id="${checkerId}"]`);
                    if (capturedChecker) {
                        capturedChecker.remove();
                    }
                });
            }
            if (data.boardData) {
                updateBoard(data.boardData);
            }
        } else if (message === 'Сейчас не ваш ход') {
            let selectedChecker = document.querySelector(`[data-checker-id="${selectedCheckerId}"]`);
            selectedChecker.classList.remove('selected');
            selectedCheckerId = null;
        }
    };

    socket.onclose = function (e) {
        console.log('Chat socket closed unexpectedly');
    };

    function handleMoveOrAttackSuccess() {
        let selectedChecker = document.querySelector(`[data-checker-id="${selectedCheckerId}"]`);
        selectedChecker.classList.remove('selected');
        selectedCheckerId = null;
        this.appendChild(selectedChecker);
    }

    cells.forEach(cell => {
        cell.addEventListener('click', function () {
            if (selectedCheckerId === null) {
                const checker = this.querySelector('.checker');
                if (checker) {
                    selectedCheckerId = checker.dataset.checkerId;
                    checker.classList.add('selected');
                }
            } else {
                const new_row = parseInt(this.parentElement.getAttribute('data-row-index'));
                const new_column = parseInt(this.getAttribute('data-cell-number'));
                var data = {
                    'checker_id': selectedCheckerId,
                    'new_row': new_row,
                    'new_column': new_column
                };

                socket.send(JSON.stringify(data));
            }
        });
    });
});

function updateBoard(boardData) {
    const cells = document.querySelectorAll('.cell');
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cellInfo = boardData[row][col];
            const cell = cells[row * 8 + col];
            const checker = cell.querySelector('.checker');

            if (cellInfo.checker_id) {
                if (!checker) {
                    const newChecker = document.createElement('span');
                    newChecker.classList.add('checker');
                    newChecker.dataset.checkerId = cellInfo.checker_id;
                    newChecker.innerText = cellInfo.checker;
                    cell.appendChild(newChecker);
                }
            } else {
                if (checker) {
                    checker.remove();
                }
            }
        }
    }
}
function getGameIdFromUrl() {
    let url = window.location.pathname;
    let urlParts = url.split('/');
    return urlParts[urlParts.length - 2];
}
