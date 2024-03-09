async function checkinTask() {
    const userName = document.getElementById('checkinUserName').value;
    const taskName = document.getElementById('checkinTaskName').value;
    const response = await fetch('http://localhost:9000/checkin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user: userName, task: taskName }),
    });

    if (response.ok) {
        document.getElementById('checkinResult').textContent = 'Task checked in successfully!';
    } else {
        const data = await response.json();
        document.getElementById('checkinResult').textContent = 'Error: ' + data.error;
    }
}

async function checkoutTask() {
    const userName = document.getElementById('checkoutUserName').value;
    const response = await fetch('http://localhost:9000/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user: userName }),
    });

    if (response.ok) {
        document.getElementById('checkoutResult').textContent = 'Task checked out successfully!';
    } else {
        const data = await response.json();
        document.getElementById('checkoutResult').textContent = 'Error: ' + data.error;
    }
}

async function generateReport() {
    const response = await fetch('http://localhost:9000/report');
    const reportDisplay = document.getElementById('reportResult');

    reportDisplay.innerHTML = '';

    if (response.status === 204) {
        reportDisplay.textContent = 'No data available.';
    } else if (response.ok) {
        const data = await response.json();
        let reportText = '';

        for (const [userName, tasks] of Object.entries(data)) {
            reportText += userName + ":\n";

            tasks.forEach(task => {
                for (const [taskName, duration] of Object.entries(task)) {
                    reportText += `  ${taskName}: ${duration}\n`;
                }
            });

            reportText += "\n";
        }

        reportDisplay.textContent = reportText;
    } else {
        const errorData = await response.json();
        reportDisplay.textContent = 'Error: ' + errorData.error;
    }
}