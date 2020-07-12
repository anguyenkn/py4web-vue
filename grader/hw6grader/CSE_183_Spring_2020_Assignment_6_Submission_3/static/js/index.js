// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
        first:[],
        p_reply:[],
        user_email
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            p.editable = true;
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
            p.is_reply = p.is_reply;
            p.email = p.email;
            p.author = p.author;
            if(p.is_reply){
                app.data.p_reply.push(p);
            }else{
                app.data.first.push(p);
            }
        }
        app.data.posts.length = 0
        for (let f of app.data.first) {
            app.data.posts.push(f)
            for (let r of app.data.p_reply) {
                if(f.id===r.is_reply){
                    app.data.posts.push(r)
                }
            }
        }
        app.data.first.length = 0
        app.data.p_reply.length = 0
        app.reindex()
        
        return app.data.posts;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };

    app.do_edit = (post_idx) => {
        if(app.isEdit()){
          let p = app.vue.posts[post_idx];
            if(user_email===p.email){
                p.edit = true;
                p.is_pending = false;
            }
        }
    };

    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            app.index(app.vue.posts);
        } else {
            // We go back to before the edit.
            p.edit = false;
            p.is_pending = false;
            p.content = p.original_content;
        }
    };

    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        console.log(post_idx);
        let p = app.vue.posts[post_idx];
        //console.log(p.id);
        //console.log(p.content);
        
        if (p.content !== p.server_content) {
            p.is_pending = true;
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
                email: p.email
            }).then((result) => {
                console.log("Received:", result.data);
                 p.edit = false;
                 p.editable = true;
                 app.index(app.vue.posts)
                 app.reindex();
                 app.init();
                //p.original_content = result.data.content;
                //p.id = result.data.id;
                //app.vue.posts.splice(p.id, 1);
                //app.vue.posts.push(p);
            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }
        
        app.reindex();

    };

    app.add_post = () => {
       
        let q = {
            id: null,
            edit: true,
            editable: true,
            content: "",
            server_content: "",
            original_content: "",
            author: "",
            email: "",
            is_reply: null
        };
       if(app.isEdit()){
        app.vue.posts.unshift(q);
       }
       
       app.reindex();
    };

    app.isEdit = () =>{
        let edit = false;
        for (let p of app.vue.posts) {
             if(p.edit){
                 edit = true;
             }
        }
      return !edit;
    }
    app.insertAt = (array, index, element) => {
        array.splice(index+1, 0, element);
    };

    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // TODO: this is the new reply.  You need to initialize it properly...
            let q = {
                id: null,
                edit: true,
                editable: true,
                content: "",
                server_content: "",
                original_content: "",
                author: "",
                email: "",
                is_reply: p.id
            };
            if(app.isEdit()){
                app.insertAt(app.vue.posts,post_idx,q ); 
            }
            app.reindex()
        }
    };
    
    

    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        
        if (p.id) {
            axios.post(delete_url, {id: p.id}).then(() => {
                app.vue.posts.splice(post_idx, 1);
                app.index(app.vue.posts);
                
            })
        }
        
    };
    
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(posts_url).then((result) => {
            app.vue.posts = app.index(result.data.posts);
            app.vue.user_email= result.data.user_email;
            
        })
        
    };
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
