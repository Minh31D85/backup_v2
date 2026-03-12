function getCSRFToken() {
    const name = "csrftoken"
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if(cookie.startsWith(name + "=")) return cookie.substring(name.length + 1);
    }
    return "";
}

function deleteBackup(path){
    fetch("/api/backups/delete/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
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