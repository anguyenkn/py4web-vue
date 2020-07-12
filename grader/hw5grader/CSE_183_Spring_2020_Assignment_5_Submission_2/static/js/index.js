// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        posts: [], // Suggested.
        new_post_content_empty: true,
        display_form: false,
        new_post_content: "",
    };

    // Add here the various functions you need.


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };

    app.reset_form = () => {
        app.vue.new_post_content = "";
        app.vue.display_form = false;
        new_post_content_empty = true;
    };

    app.add_post = () => {
        new_post_content_empty = Boolean(app.vue.new_post_content.trim().length === 0)
        if (!new_post_content_empty) {
            axios.post(add_post_url, {
                new_post_content: app.vue.new_post_content,
            }).then(function (response) {
                app.reset_form();
                app.init();
            });
        }
    }

    app.delete_post = (idx) => {
        axios.post(delete_post_url, {
            id: idx,
        }).then(function (response) {
            app.init();
        });
    }

    app.thumb_post = (p, rating) => {
        p.liked = Boolean(rating == 1);
        p.disliked = Boolean(rating == -1);
        axios.post(thumb_post_url, {
            id: p.id,
            rating: rating
        }).then(function (response) {
            axios.post(get_thumbs_url, {
                id: p.id,
            }).then(function (result) {
                p.show_likers = true;
                p.liked_by = result.data.liked_by;
                p.disliked_by = result.data.disliked_by;
            });
        });
    }

    app.show_thumbs = (p) => {
        if (p.cache_likes) {
            p.show_likers = true;
            return;
        }
        axios.post(get_thumbs_url, {
            id: p.id,
        }).then(function (result) {
            p.show_likers = true;
            p.liked_by = result.data.liked_by;
            p.disliked_by = result.data.disliked_by;
            p.cache_likes = true;
        });
    }

    app.hide_thumbs = (p) => {
        p.show_likers = false;
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        add_post: app.add_post,
        reset_form: app.reset_form,
        delete_post: app.delete_post,
        thumb_post: app.thumb_post,
        show_thumbs: app.show_thumbs,
        hide_thumbs: app.hide_thumbs
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_posts_url).then((result) => {
            app.vue.posts = result.data.posts;
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
