// Add any interactive JavaScript functionality here

document.getElementById("comment-form").addEventListener("submit", function(event) {
    event.preventDefault();
    var userName = document.getElementById("user-name").value;
    var commentText = document.getElementById("comment-text").value;
    var commentContainer = document.querySelector(".comments");
    var newComment = document.createElement("div");
    newComment.classList.add("comment");
    newComment.innerHTML = `
        <p class="user">${userName}</p>
        <p class="comment-text">${commentText}</p>
    `;
    commentContainer.appendChild(newComment);
    document.getElementById("user-name").value = "";
    document.getElementById("comment-text").value = "";
});
