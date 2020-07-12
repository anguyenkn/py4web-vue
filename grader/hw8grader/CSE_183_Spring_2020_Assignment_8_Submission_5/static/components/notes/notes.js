(function(){

    var notes = {
        props: ["get_all_notes", "create_new_note", "edit_note_key", "delete_note"],
        data: {},
        methods: {}
    };

    const colors = ["red", "yellow", "green", "blue", "purple"];

    notes.data = function() {
        var data ={
            urls: {                                  // url object in data
                get_all: this.get_all_notes, 
                create_new: this.create_new_note,
                delete_note: this.delete_note,
                edit_key: this.edit_note_key
            },
            notes: [],
            colors
        };
        notes.methods.load.call(data);
        return data;
    };

    notes.methods.load = function() {
        let self = this;
        axios.get(self.urls.get_all).then((response) => {
            let notes = response.data.notes;
            notes.forEach((note) => (note.edit = false));
            self.notes = notes;
            reindex(self.notes);
        }).catch((error) => {
            console.log("error: ");
            console.log(error);
        });
    };

    notes.methods.create = function() {
        let self = this;
        axios.get(self.urls.create_new).then((response) => {
            let note = response.data.note;
            note.edit = false;
            self.notes.unshift(note);
            reindex(self.notes);
        }).catch((error) => {
            console.log("error: ");
            console.log(error);
        });
    };

    notes.methods.edit_key = function (idx, key, val) {
        let self = this;
        axios.post(self.urls.edit_key, {
            id: self.notes[idx].id,
            key: key,
            val: val
        }).then((response) => {
            self.notes[idx] = {
                ...response.data.note,
                _idx: idx,
                edit: true
            };
            this.refresh();
        }).catch((error) => {
            console.log("error: ");
            console.log(error);
        });
    };

    notes.methods.remove = function(idx) {
        let self = this;
        let id = self.notes[idx].id;
        axios.post(self.urls.delete_note, { id }).then((response) =>{
            this.notes.splice(idx, 1);
            reindex(self.notes);
        })
    };

    notes.methods.refresh = function() {
        this.$forceUpdate();
    };

    notes.methods.color_class = function(index) {
        return "pastel-" + this.colors[index];
    };

    notes.methods.sort_notes = function() {
        let starred = this.notes.filter((note) => note.has_star === true);
        let not_starred = this.notes.filter((note) => note.has_star === false);

        return [...sort_date(starred), ...sort_date(not_starred)];

    }

    function reindex(items) {
        for(let i = 0; i < items.length; i++)
            items[i]._idx = i;
    }

    function sort_date(items) {
        return items.sort(function(a,b) {
            return new Date(b.last_modified) - new Date(a.last_modified);
        });
    }

    notes.methods.format_note_text = function(content, idx) {
        if(this.notes[idx].is_list) {
            return content
                .split("\n")
                .map((item, index, arr) => {
                    let format = "- " + item;
                    return format;
                })
                .join("\n");
        } else return content;
    };

    notes.methods.handle_note_change = function (event, idx) {
        let clean = event.target.value.replace(/\- /g, "").replace(/\-/g, "");
        this.notes[idx].content = clean;
        this.edit_key(idx, "content", clean);
    };


    notes.methods.toggle_edit = function(bool, idx) {
        if (bool == true) {
            this.notes.forEach((note) => (note.edit = false));
        }
        this.notes[idx].edit = bool;
    }

    utils.register_vue_component(
        "notes", 
        "components/notes/notes.html", 
        function(template) {
            notes.template = template.data;
            return notes;
        }
    );


})();
