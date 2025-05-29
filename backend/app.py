from flask import Flask, request, jsonify
from flask_cors import CORS # Import Flask-CORS
from core.task import Task
from core.graph import Graph
from core.algorithm import TopologicalSorter, CycleDetectedError

app = Flask(__name__)
CORS(app)

task_graph = Graph()
sorter = TopologicalSorter(task_graph)

# Dummy Data
def add_dummy_data():
    """Menambahkan beberapa tugas dan dependensi awal ke graf."""
    tasks_to_add = [
        Task(task_id="t1", name="Riset Kebutuhan", description="Mengumpulkan kebutuhan pengguna dan pasar."),
        Task(task_id="t2", name="Desain UI/UX", description="Membuat mockup dan prototipe antarmuka."),
        Task(task_id="t3", name="Setup Backend", description="Mengkonfigurasi server dan database."),
        Task(task_id="t4", name="Implementasi API", description="Membuat endpoint API untuk frontend."),
        Task(task_id="t5", name="Pengembangan Frontend", description="Membangun antarmuka pengguna berdasarkan desain."),
        Task(task_id="t6", name="Integrasi", description="Menghubungkan frontend dan backend."),
        Task(task_id="t7", name="Testing", description="Melakukan pengujian unit, integrasi, dan pengguna."),
        Task(task_id="t8", name="Deployment", description="Menerbitkan aplikasi ke server produksi.")
    ]

    for task in tasks_to_add:
        task_graph.add_task(task)

    dependencies_to_add = [
        ("t1", "t2"), # Riset Kebutuhan -> Desain UI/UX
        ("t2", "t5"), # Desain UI/UX -> Pengembangan Frontend
        ("t3", "t4"), # Setup Backend -> Implementasi API
        ("t4", "t6"), # Implementasi API -> Integrasi
        ("t5", "t6"), # Pengembangan Frontend -> Integrasi
        ("t6", "t7"), # Integrasi -> Testing
        ("t7", "t8")  # Testing -> Deployment
    ]

    for prereq_id, task_id in dependencies_to_add:
        task_graph.add_dependency(prereq_id, task_id)
    
    app.logger.info("Data dummy berhasil ditambahkan ke graf.")

add_dummy_data()


@app.route('/api/tasks', methods=['POST'])
def add_task_api():
    data = request.get_json()
    if not data or 'name' not in data: 
        return jsonify({"error": "Payload JSON tidak valid atau 'name' tidak ada"}), 400
    
    task_name = data.get('name')
    task_id = data.get('id', task_name)
    description = data.get('description', "")

    if not task_name:
        return jsonify({"error": "Nama tugas tidak boleh kosong"}), 400
    if not task_id:
        return jsonify({"error": "ID tugas tidak boleh kosong"}), 400

    new_task = Task(task_id=task_id, name=task_name, description=description)
    
    success = task_graph.add_task(new_task)

    if success:
        return jsonify({
            "message": "Tugas berhasil ditambahkan", 
            "task": new_task.to_dict()
        }), 201
    else:
        return jsonify({"error": f"Tugas dengan ID '{task_id}' sudah ada atau terjadi kesalahan."}), 409

@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    tasks_data = task_graph.get_all_tasks_with_dependencies_info()
    return jsonify(tasks_data), 200

@app.route('/api/dependencies', methods=['POST'])
def add_dependency_api():
    data = request.get_json()
    if not data or 'task_id' not in data or 'prerequisite_id' not in data:
        return jsonify({"error": "Payload JSON tidak valid atau 'task_id'/'prerequisite_id' tidak ada"}), 400

    task_id = data.get('task_id')
    prerequisite_id = data.get('prerequisite_id')

    if not task_id or not prerequisite_id:
        return jsonify({"error": "ID tugas dan ID prasyarat diperlukan dan tidak boleh kosong"}), 400

    if task_id == prerequisite_id:
        return jsonify({"error": "Tugas tidak dapat bergantung pada dirinya sendiri"}), 400

    success = task_graph.add_dependency(prerequisite_id, task_id)

    if success:
        return jsonify({"message": "Dependensi berhasil ditambahkan"}), 201
    else:
        msg = "Gagal menambah dependensi. Pastikan kedua ID tugas ada dan tidak menyebabkan siklus langsung."

        if not task_graph.get_task(prerequisite_id):
            msg = f"Gagal menambah dependensi. Prasyarat dengan ID '{prerequisite_id}' tidak ditemukan."
        elif not task_graph.get_task(task_id):
            msg = f"Gagal menambah dependensi. Tugas dengan ID '{task_id}' tidak ditemukan."
        return jsonify({"error": msg}), 400

@app.route('/api/sort', methods=['GET'])
def sort_tasks_api():
    try:
        sorted_task_ids = sorter.sort()
        
        sorted_tasks_details = []
        for task_id in sorted_task_ids:
            task_obj = task_graph.get_task(task_id)
            if task_obj:
                sorted_tasks_details.append(task_obj.to_dict())
            else:
                sorted_tasks_details.append({"id": task_id, "name": task_id, "error": "Detail tidak ditemukan"})

        return jsonify({"sorted_tasks": sorted_tasks_details, "error": None}), 200
    except CycleDetectedError as e:
        app.logger.warning(f"Cycle detected during sort: {e}")
        return jsonify({"sorted_tasks": [], "error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error during sort: {e}", exc_info=True)
        return jsonify({"sorted_tasks": [], "error": "Terjadi kesalahan internal pada server saat mengurutkan."}), 500

@app.route('/api/tasks/<string:task_id_to_delete>', methods=['DELETE'])
def delete_task_api(task_id_to_delete):
    if not task_id_to_delete:
        return jsonify({"error": "ID Tugas diperlukan untuk penghapusan"}), 400

    success = task_graph.remove_task(task_id_to_delete)

    if success:
        return jsonify({"message": f"Tugas '{task_id_to_delete}' dan dependensi terkait berhasil dihapus."}), 200
    else:
        return jsonify({"error": f"Tugas dengan ID '{task_id_to_delete}' tidak ditemukan."}), 404 # Not Found

@app.route('/api/reset', methods=['POST'])
def reset_api():
    global task_graph, sorter
    
    task_graph = Graph()
    sorter = TopologicalSorter(task_graph)
    
    add_dummy_data()
    
    app.logger.info("Graf tugas berhasil direset dan data dummy ditambahkan kembali.")
    return jsonify({"message": "Graf tugas berhasil direset dan data dummy ditambahkan kembali."}), 200

if __name__ == '__main__':
    print("Menjalankan server Flask untuk Task Dependency Manager...")
    print("Menggunakan implementasi core dari direktori 'core/'.")
    if not task_graph.get_all_task_ids():
        print("PERHATIAN: Data dummy sepertinya tidak termuat. Memanggil add_dummy_data() lagi.")
        add_dummy_data()
    else:
        print(f"Data dummy telah dimuat. Jumlah tugas awal: {len(task_graph.get_all_task_ids())}")
        
    app.run(debug=True, port=5001)