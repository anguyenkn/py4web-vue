(function () {
    let note = {
        props: ['note_object'],
        data: null,
        methods: {}
    };
    note.data = function () {
        let data = {
            note_title: this.note_object.title,
            note_content: this.note_object.content,
            note_color: this.note_object.color,
            is_pinned: this.note_object.pinned,
            edit_status: this.note_object.edit,
            content_empty: false
        };
        return data;
    };
    note.methods.star_click = function () {
        this.is_pinned = !this.is_pinned;
        this.$emit('note_pinned');
        do_save.call(this);
    };
    note.methods.change_color = function (color) {
        if (color === this.note_color)
            this.note_color = 'is-white';
        else
            this.note_color = color;
        do_save.call(this);
    };
    note.methods.save_note = function () {
        this.edit_status = 0;
        do_save.call(this);
    };
    note.methods.delete_note = function () {
        this.$emit('delete_note', this.edit_status);
        this.edit_status = 0;
    };
    let do_save = function () {
        axios.post(notes_url, {
            id: this.note_object.id,
            title: this.note_title,
            content: this.note_content,
            note_date: this.note_object.note_date,
            color: this.note_color,
            pinned: this.is_pinned
        }).then(response => {
            if (!this.id) {
                this.$emit('new_note', response.data.id); //to send id to index.js
            }
        })
    };
    utils.register_vue_component('note', 'components/note/note.html',
        function (template) {
            note.template = template.data;
            return note;
        });
})();
