function deleteBackup(path){
    fetch("/api/backups/delete/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({ path: path})
    })
    .then(response => {
        if(!response.ok) throw new Error("Delete failed");
        return response.json();
    })
    .then(data => {
        alert("Backup gelöscht: " + data.path);
        location.reload();
    })
    .catch(() => {
        alert("Fehler beim Löschen des Backups")
    })
}