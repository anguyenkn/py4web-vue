// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        add_post_contents: "",
        posts: [],
        show_field: false,
        // Complete.
    };

    // Add here the various functions you need.


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a, thumbs) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
            p.show_like = false;
            p.show_dislike = false;
            p.liked_list = [];
            p.disliked_list = [];
            // TODO Like and dislike list
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };


    // Add a post
    app.add_post = () => {
        let error = false;
        if (app.vue.add_post_contents.trim().length === 0) {
            error = true;
        }

        if (!error) {
            app.perform_insertion();
        }
        app.vue.show_field = false;
    };

    app.perform_insertion = () => {
        // Add post and display
        axios.post(add_post_url, {
            post_contents: app.vue.add_post_contents,
        }).then(function (response) {
            app.vue.posts.push({
                id: response.data.id,
                name: response.data.name,
                post_text: app.vue.add_post_contents,
                show_like: false,
                show_dislike: false,
                liked_list: [],
                disliked_list: [],
                user_email: user_email,
            });
            app.reindex(app.vue.posts);

            app.vue.add_post_contents = "";

            // Close post form TODO
        });
    }


    // Delete post
    app.delete_post = (id, post) => {
        axios.post(delete_post_url, {
            post_id: id,
        }).then(function (response) {
            if (response.data.deleted === 1) {
                app.vue.posts.forEach((post, index) => {
                    if (post.id == id) {
                        app.vue.$delete(app.vue.posts, index);
                    }
                });
            }
            app.reindex(app.vue.posts);
        });
    };


    // Cancel post
    app.cancel_post = () => {
        app.vue.add_post_contents = "";
        app.vue.show_field = false;
    };


    // Open post field
    app.open_post_field = () => {
        app.vue.show_field = true;
    };

    
    // Clicked like
    app.click_like = (post) => {
        console.log(post.id);
        axios.post(like_post_url, {post_id: post.id,}).then((result) => {
            post.like_status = result.data.rating;

            // Edit liked list
            if (result.data.rating == 0) {
                post.liked_list = post.liked_list.filter(function(v, i, a) {
                     return v != result.data.name; 
                    });
            }
            else {
                post.liked_list.push(result.data.name);
                post.disliked_list = post.liked_list.filter(function(v, i, a) {
                    return v != result.data.name; 
                   });
            }
        });
    }

    // Clicked dislike
    app.click_dislike = (post) => {
        axios.post(dislike_post_url, {post_id: post.id,}).then((result) => {
            post.like_status = result.data.rating;

            // Edit disliked list
            if (result.data.rating == 0) {
                post.disliked_list = post.liked_list.filter(function(v, i, a) {
                     return v != result.data.name; 
                    });
            }
            else {
                post.disliked_list.push(result.data.name);
                post.liked_list = post.liked_list.filter(function(v, i, a) {
                    return v != result.data.name; 
                   });
            }
        });
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        add_post: app.add_post,
        delete_post: app.delete_post,
        cancel_post: app.cancel_post,
        open_post_field: app.open_post_field,
        click_like: app.click_like,
        click_dislike: app.click_dislike,
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
            app.vue.posts = app.reindex(result.data.posts);
            app.vue.posts.forEach(post => {
                post.like_status = 0;
                result.data.thumbs.forEach(thumb => {
                    if (thumb.post_id === post.id) {
                        // Liked or disliked stuff
                        if (thumb.rating === 1) {
                            post.liked_list.push(thumb.name);
                        }
                        if (thumb.rating === -1) {
                            post.disliked_list.push(thumb.name);
                        }

                        // Rating stuff
                        if (thumb.user_email === user_email) {
                            post.like_status = thumb.rating;
                        }
                    }
                });
            });
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
