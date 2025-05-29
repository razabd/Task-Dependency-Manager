document.addEventListener('DOMContentLoaded', () => {
    // Elemen UI dari HTML baru
    const taskNameInput = document.getElementById('taskNameInput');
    const taskDescriptionInput = document.getElementById('taskDescriptionInput');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const prerequisiteSelect = document.getElementById('prerequisiteSelect');
    const taskSelect = document.getElementById('taskSelect'); // Ini untuk tugas yang bergantung
    const addDependencyBtn = document.getElementById('addDependencyBtn');
    const taskListUl = document.getElementById('taskList');
    const sortTasksBtn = document.getElementById('sortTasksBtn');
    const sortedTasksResultDiv = document.getElementById('sortedTasksResult');
    const errorMessagesDiv = document.getElementById('errorMessages');
    const successMessagesDiv = document.getElementById('successMessages');
    const resetGraphBtn = document.getElementById('resetGraphBtn');


    const API_BASE_URL = 'http://localhost:5001/api'; // Sesuaikan dengan URL backend Anda

    let allTasksData = []; // Simpan semua data tugas di sini untuk referensi

    async function fetchTasks() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
                throw new Error(errorData.error);
            }
            const tasks = await response.json();
            allTasksData = tasks;
            updateTaskList(allTasksData);
            updateSelectOptions(allTasksData);
        } catch (error) {
            displayMessage(`Gagal memuat tugas: ${error.message}`, 'error');
        }
    }

    function updateTaskList(tasks) {
        taskListUl.innerHTML = ''; 
        if (tasks && tasks.length > 0) {
            tasks.forEach(task => {
                const li = document.createElement('li');
                
                const taskInfoDiv = document.createElement('div'); // Div untuk info tugas
                taskInfoDiv.classList.add('flex-grow'); // Agar mengambil sisa ruang

                let taskHtml = `<div class="font-semibold">${task.name} <span class="text-xs text-gray-500">(ID: ${task.id})</span></div>`;
                if (task.description) {
                    taskHtml += `<div class="text-sm text-gray-600 mt-1">Deskripsi: ${task.description}</div>`;
                }
                if (task.dependencies && task.dependencies.length > 0) {
                    const prerequisiteNames = task.dependencies.map(depId => {
                        const prereqTask = allTasksData.find(t => t.id === depId);
                        return prereqTask ? prereqTask.name : depId;
                    });
                    taskHtml += `<div class="text-sm text-blue-600 mt-1">Prasyarat: ${prerequisiteNames.join(', ')}</div>`;
                } else {
                    taskHtml += `<div class="text-sm text-gray-500 mt-1">Prasyarat: Tidak ada</div>`;
                }
                taskInfoDiv.innerHTML = taskHtml;
                li.appendChild(taskInfoDiv);

                const deleteButton = document.createElement('button');
                deleteButton.innerHTML = '<i class="ph-trash text-red-500 hover:text-red-700 text-lg"></i>'; // Perbesar ikon sedikit
                deleteButton.classList.add('ml-2', 'p-1', 'rounded', 'hover:bg-red-100', 'transition-colors', 'flex-shrink-0'); // flex-shrink-0 agar tombol tidak mengecil
                deleteButton.title = `Hapus tugas ${task.name}`;
                deleteButton.onclick = () => deleteTask(task.id, task.name);
                li.appendChild(deleteButton);

                taskListUl.appendChild(li);
            });
        } else {
            taskListUl.innerHTML = '<li class="p-3 bg-gray-50 rounded-md justify-center">Tidak ada tugas saat ini.</li>';
        }
    }

    function updateSelectOptions(tasks) {
        const defaultOptionTextTask = "Pilih tugas yang bergantung...";
        const defaultOptionTextPrereq = "Pilih tugas prasyarat...";

        taskSelect.innerHTML = `<option value="">${defaultOptionTextTask}</option>`;
        prerequisiteSelect.innerHTML = `<option value="">${defaultOptionTextPrereq}</option>`;

        if (tasks && tasks.length > 0) {
            tasks.forEach(task => {
                const option1 = new Option(`${task.name} (ID: ${task.id})`, task.id);
                const option2 = new Option(`${task.name} (ID: ${task.id})`, task.id);
                taskSelect.add(option1);
                prerequisiteSelect.add(option2);
            });
        }
    }

    function displayMessage(message, type = 'error') {
        const targetDiv = type === 'error' ? errorMessagesDiv : successMessagesDiv;
        const otherDiv = type === 'error' ? successMessagesDiv : errorMessagesDiv;

        targetDiv.textContent = message;
        targetDiv.style.display = 'block';
        otherDiv.style.display = 'none'; 

        setTimeout(() => {
            targetDiv.style.display = 'none';
            targetDiv.textContent = '';
        }, 5000); 
    }
    
    const displayError = (message) => displayMessage(message, 'error');
    const displaySuccess = (message) => displayMessage(message, 'success');


    function clearMessages() { // Fungsi ini mungkin tidak lagi diperlukan jika displayMessage menangani timeout
        errorMessagesDiv.textContent = '';
        errorMessagesDiv.style.display = 'none';
        successMessagesDiv.textContent = '';
        successMessagesDiv.style.display = 'none';
    }

    function clearResult() {
        sortedTasksResultDiv.innerHTML = '<p class="p-3 bg-gray-50 rounded-md">Klik tombol di atas untuk melihat hasil pengurutan.</p>';
    }

    addTaskBtn.addEventListener('click', async () => {
        // clearMessages(); // displayMessage akan menangani ini
        const taskName = taskNameInput.value.trim();
        const taskDescription = taskDescriptionInput.value.trim();
        const taskId = taskName.toLowerCase().replace(/\s+/g, '_').replace(/[^\w-]/g, '') || `task_${Date.now()}`;


        if (!taskName) {
            displayError('Nama tugas tidak boleh kosong.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: taskId, name: taskName, description: taskDescription })
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            taskNameInput.value = '';
            taskDescriptionInput.value = '';
            displaySuccess(result.message || 'Tugas berhasil ditambahkan!');
            fetchTasks();
        } catch (error) {
            displayError(`Gagal menambah tugas: ${error.message}`);
        }
    });

    addDependencyBtn.addEventListener('click', async () => {
        // clearMessages();
        const dependentTaskId = taskSelect.value; 
        const prerequisiteTaskId = prerequisiteSelect.value;

        if (!dependentTaskId || !prerequisiteTaskId) {
            displayError('Pilih tugas dan prasyaratnya.');
            return;
        }
        if (dependentTaskId === prerequisiteTaskId) {
            displayError('Tugas tidak dapat bergantung pada dirinya sendiri.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/dependencies`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: dependentTaskId, prerequisite_id: prerequisiteTaskId })
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            displaySuccess(result.message || 'Dependensi berhasil ditambahkan!');
            fetchTasks();
            taskSelect.value = "";
            prerequisiteSelect.value = "";
        } catch (error) {
            displayError(`Gagal menambah dependensi: ${error.message}`);
        }
    });

    sortTasksBtn.addEventListener('click', async () => {
        // clearMessages();
        clearResult(); // Hanya bersihkan area hasil sort sebelumnya
        try {
            const response = await fetch(`${API_BASE_URL}/sort`);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

            if (result.error) {
                 displayMessage(`Error saat sorting: ${result.error}`, 'error'); 
                 sortedTasksResultDiv.innerHTML = `<p class="p-3 bg-red-50 text-red-700 rounded-md">Gagal mengurutkan tugas: ${result.error}</p>`;
            } else if (result.sorted_tasks && result.sorted_tasks.length > 0) {
                let htmlResult = '<h3 class="text-lg font-medium text-gray-700 mb-3">Urutan Tugas yang Direkomendasikan:</h3><ol class="list-decimal list-inside space-y-1">';
                result.sorted_tasks.forEach(task => {
                    htmlResult += `<li class="p-2 bg-green-50 border-l-4 border-green-500 rounded-r-md">${task.name} <span class="text-xs text-gray-500">(ID: ${task.id})</span></li>`;
                });
                htmlResult += '</ol>';
                sortedTasksResultDiv.innerHTML = htmlResult;
                displaySuccess('Urutan tugas berhasil ditampilkan.'); // Pesan sukses untuk sort
            } else {
                sortedTasksResultDiv.innerHTML = '<p class="p-3 bg-gray-50 rounded-md">Tidak ada tugas untuk diurutkan atau tidak ada urutan yang valid ditemukan.</p>';
                 displayMessage('Tidak ada tugas untuk diurutkan atau tidak ada urutan valid.', 'error'); // Pesan jika tidak ada hasil
            }
        } catch (error) {
            displayMessage(`Error saat sorting: ${error.message}`, 'error');
            sortedTasksResultDiv.innerHTML = `<p class="p-3 bg-red-50 text-red-700 rounded-md">Gagal mengurutkan tugas: ${error.message}</p>`;
        }
    });

    async function deleteTask(taskId, taskName) {
        // clearMessages();
        if (!confirm(`Anda yakin ingin menghapus tugas "${taskName}" (ID: ${taskId})? Ini juga akan menghapus semua dependensi yang terkait dengannya.`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: 'DELETE',
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            displaySuccess(result.message || `Tugas "${taskName}" berhasil dihapus.`);
            fetchTasks(); 
            clearResult(); 
        } catch (error) {
            displayError(`Gagal menghapus tugas: ${error.message}`);
        }
    }
    
    resetGraphBtn.addEventListener('click', async () => {
        // clearMessages();
        if (!confirm("Anda yakin ingin mereset semua tugas dan dependensi? Data dummy akan dimuat ulang.")) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/reset`, {
                method: 'POST',
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            displaySuccess(result.message || "Semua tugas berhasil direset dan data dummy dimuat ulang.");
            fetchTasks(); 
            clearResult(); 
        } catch (error) {
            displayError(`Gagal mereset tugas: ${error.message}`);
        }
    });

    fetchTasks();
});