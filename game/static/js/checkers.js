document.addEventListener('DOMContentLoaded', function () {
    const cells = document.querySelectorAll('.cell');
    let selectedCheckerId = null;
    let socket = null;

    cells.forEach(cell => {
        cell.addEventListener('click', function () {
            const checker = this.querySelector('.checker');

            if (selectedCheckerId === null) {
                if (checker) {
                    selectedCheckerId = checker.dataset.checkerId;
                    checker.classList.add('selected');
                }
            } else {
                if (!checker) {
                    const selectedChecker = document.querySelector(`[data-checker-id="${selectedCheckerId}"]`);
                    if (selectedChecker) {
                        const new_row = parseInt(this.parentElement.getAttribute('data-row-index'));
                        const new_column = parseInt(this.getAttribute('data-cell-number'));
                        sendMoveData(selectedCheckerId, new_row, new_column);
                        console.log(selectedCheckerId, new_row, new_column)
                    }
                } else {
                    selectedCheckerId = null;
                    checker.classList.remove('selected');
                }
            }
        });
    });

    function connectWebSocket() {
        game_id = getGameIdFromUrl()
        const socket = new WebSocket(`ws://` + window.location.host + `/ws/`);

        socket.onopen = function (event) {
            console.log('JS: socket open');
        };

        socket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);

            if (data.message === 'Успешный ход' || data.message === 'Успешная атака') {
                handleMoveOrAttackSuccess(data);
            } else if (data.message === 'Сейчас не ваш ход') {
                handleNotYourTurn();
            }
        };

        socket.onclose = function (event) {
            console.log('WebSocket connection closed.');
        };

        socket.onerror = function (event) {
            console.error('WebSocket error:', event);
        };

        function handleMoveOrAttackSuccess(data) {
            const new_row = data.new_row;
            const new_column = data.new_column;
            const cell = document.querySelector(`[data-row-index="${new_row}"][data-cell-number="${new_column}"]`);
            const checker = cell.querySelector('.checker');

            if (data.message === 'Успешная атака') {
                const captured_checkers = data.captured_checkers;
                captured_checkers.forEach(checkerId => {
                    const capturedChecker = document.querySelector(`[data-checker-id="${checkerId}"]`);
                    if (capturedChecker) {
                        capturedChecker.remove();
                    }
                });
            }

            if (checker) {
                checker.remove();
            }
            if (data.boardData) {
                updateBoard(data.boardData);
            }
        }

        function handleNotYourTurn() {
            if (selectedCheckerId !== null) {
                const selectedChecker = document.querySelector(`[data-checker-id="${selectedCheckerId}"]`);
                selectedChecker.classList.remove('selected');
                selectedCheckerId = null;
            }
        }

        return socket
    }

    function getGameIdFromUrl() {
        const url = window.location.pathname;
        const urlParts = url.split('/');
        return urlParts[urlParts.length - 2];
    }

    function sendMoveData(checkerId, newRow, newColumn) {
            const data = {
                'command': 'move',
                'checker_id': checkerId,
                'new_row': newRow,
                'new_column': newColumn
            };
            socket.send(JSON.stringify(data));
        }

    connectWebSocket();

})