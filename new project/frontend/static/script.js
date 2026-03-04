document.addEventListener('DOMContentLoaded', () => {

    // AI Analysis Preview
    const analyzeBtn = document.getElementById('analyze-btn');
    const descriptionInput = document.getElementById('description');
    const previewBox = document.getElementById('ai-preview');
    const previewText = document.getElementById('preview-text');

    const BACKEND_URL = "https://ai-incident-manager.onrender.com"; // replace if your URL is different

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const text = descriptionInput.value;

            if (!text.trim()) {
                alert("Please enter a description first.");
                return;
            }

            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            try {

                const response = await fetch(`${BACKEND_URL}/api/analyze`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ description: text })
                });

                const result = await response.json();

                previewBox.style.display = 'block';

                let priorityClass = 'text-white';

                if (result.priority === 'High') {
                    priorityClass = 'text-red-400';
                }

                if (result.priority === 'Medium') {
                    priorityClass = 'text-yellow-400';
                }

                if (result.priority === 'Low') {
                    priorityClass = 'text-green-400';
                }

                let html = `
                    <strong>Predicted Priority:</strong> 
                    <span class="${priorityClass}">${result.priority}</span><br>
                `;

                if (result.is_major_candidate) {
                    html += `
                        <strong style="color:#ef4444;">Warning:</strong>
                        Existing similar incidents found! This might be a Major Incident.
                    `;
                } else {
                    html += `No similar major incidents detected.`;
                }

                previewText.innerHTML = html;

            } catch (error) {

                console.error("Error analyzing:", error);
                alert("Failed to analyze text. Please try again.");

            } finally {

                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Check Priority';

            }
        });
    }

});

