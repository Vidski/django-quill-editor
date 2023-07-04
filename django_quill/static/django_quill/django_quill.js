Quill.register("modules/imageCompressor", imageCompressor);
Quill.register("modules/resize", window.QuillResizeModule);
Quill.register("modules/imageUploader", ImageUploader)
Quill.register('modules/quillMention', quillMention);

class QuillWrapper {
    constructor(targetDivId, targetInputId, quillOptions) {
        this.targetDiv = document.getElementById(targetDivId);
        if (!this.targetDiv) throw 'Target div(' + targetDivId + ') id was invalid';

        this.targetInput = document.getElementById(targetInputId);
        if (!this.targetInput) throw 'Target Input id was invalid';

        if (quillOptions['modules']['imageUploader']) {
            quillOptions['modules']['imageUploader'] = {
                upload: (file) => {
                    return new Promise((resolve, reject) => {
                        const formData = new FormData();
                        formData.append("image", file);
                        fetch(
                            quillOptions['uploadUrl'],
                            {
                                method: "POST",
                                body: formData
                            }
                        )
                            .then((response) => response.json())
                            .then((result) => {
                                console.log(result);
                                resolve(result.url);
                            })
                            .catch((error) => {
                                reject("Upload failed");
                                console.error("Error:", error);
                            });
                    });
                }
            }
        }

        if (quillOptions['modules']['mention']) {
            quillOptions['modules']['mention'] = {
                allowedChars: /^[A-Za-z\sÅÄÖåäö]*$/,
                mentionDenotationChars: ["@", "#"],
                source: function (searchTerm, renderList, mentionChar) {
                    let values;
                    let endpoint;

                    if (mentionChar === "@" && quillOptions['modules']['mention']['mention'] === true) {
                        endpoint = `${quillOptions['mentionsUrl']}?search=${searchTerm}`;
                    } else if (mentionChar === "#" && quillOptions['modules']['mention']['tags'] === true) {
                        endpoint = `${quillOptions['tagsUrl']}?name__icontains=${searchTerm}`;
                    }

                    fetch(endpoint)
                        .then(response => response.json())
                        .then(data => {
                            values = data.results;
                            if (searchTerm.length === 0) {
                                renderList(values, searchTerm);
                            } else {
                                const matches = [];
                                for (let i = 0; i < values.length; i++)
                                    if (~values[i].value.toLowerCase().indexOf(searchTerm.toLowerCase()))
                                        matches.push(values[i]);
                                renderList(matches, searchTerm);
                            }
                        })
                        .catch((error) => {
                            console.error("Error:", error);
                        });
                }
            }
        }

        this.quill = new Quill('#' + targetDivId, quillOptions);
        this.quill.on('text-change', () => {
            var delta = this.quill.getContents();
            var html = this.targetDiv.getElementsByClassName('ql-editor')[0].innerHTML;
            var data = {
                delta: delta,
                html: html
            };
            this.targetInput.value = JSON.stringify(data);
        });
    }
}
