function togglePopup(action, id=0) {
  if (action === 'add') {
    const addForm = document.getElementById('popupOverlayAdd');
    addForm.classList.toggle('show');
  }
  else if (action === 'edit') {
    const editForm = document.getElementById('popupOverlayEdit' + id);
    editForm.classList.toggle('show');
  }
  else if (action === 'remove') {
    const removeForm = document.getElementById('popupOverlayRemove' + id);
    removeForm.classList.toggle('show');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const imageUpload = document.getElementById('dropzone-file');
  imageUpload.addEventListener('change', function() {
    const image = imageUpload.files[0];
    const reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = function(e) {
      const imageDataUrl = e.target.result;
      const imagePreview = document.getElementById('imagePreview');
      imagePreview.src = imageDataUrl;
      imagePreview.classList.remove('hidden');
    };
  });
});
