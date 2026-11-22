
document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        const fileInput = form.querySelector('input[type="file"]');

        // Create file information area
        const fileInfo = document.createElement("p");
        fileInfo.className = "file-info text-primary mt-2";
        fileInput.insertAdjacentElement("afterend", fileInfo);

        // Display selected file
        fileInput.addEventListener("change", function () {
            const file = fileInput.files[0];

            if (!file) {
                fileInfo.textContent = "";
                return;
            }

            const extension = "." + file.name.split(".").pop().toLowerCase();
            const allowed = fileInput.accept.split(",").map(x => x.trim());

            if (!allowed.includes(extension)) {
                alert("Please select a valid file.");
                fileInput.value = "";
                fileInfo.textContent = "";
                return;
            }

            if (file.size > 25 * 1024 * 1024) {
                alert("File size must be less than 25 MB.");
                fileInput.value = "";
                fileInfo.textContent = "";
                return;
            }

            fileInfo.textContent = "Selected: " + file.name;
        });

        // Drag and drop
        fileInput.addEventListener("dragover", function (event) {
            event.preventDefault();
            fileInput.classList.add("drag-active");
        });

        fileInput.addEventListener("dragleave", function () {
            fileInput.classList.remove("drag-active");
        });

        fileInput.addEventListener("drop", function (event) {
            event.preventDefault();
            fileInput.classList.remove("drag-active");

            const files = event.dataTransfer.files;

            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event("change"));
            }
        });

        // Upload progress
        form.addEventListener("submit", function (event) {

            if (!fileInput.files.length) {
                event.preventDefault();
                alert("Please select a file first.");
                return;
            }

            const button = form.querySelector("button[type='submit']");
            button.disabled = true;
            button.textContent = "Uploading and converting...";

            const progress = document.createElement("div");
            progress.className = "progress mt-3";
            progress.innerHTML = `
                <div class="progress-bar progress-bar-striped progress-bar-animated"
                     role="progressbar" style="width: 100%">
                     Processing...
                </div>
            `;

            form.appendChild(progress);
        });

    });

});
