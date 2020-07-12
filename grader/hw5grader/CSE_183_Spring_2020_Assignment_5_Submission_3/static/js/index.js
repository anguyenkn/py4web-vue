// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        username: username,
        posts: [], // Suggested.
        // Complete.
        add_post_text: "",
        page: "adding",
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
    
    app.add_post = () => {
        app.perform_insertion();
    };
    
    app.perform_insertion = () => {
        axios.post(add_posts_url, {
            post_text: app.vue.add_post_text,
        }).then(function (response) {
            //Using unshift because it places the post at the top, rather
            //than pushing it at the bottom. 
            app.vue.posts.unshift({  
                id: response.data.id, 
                post_text: app.vue.add_post_text,
                rating: 0,
                show_likers: 0,
                likers: "",
                dislikers: "",
                show_dislikers: 0, 
                usernames: app.data.username,
                user_email: app.data.user_email,
                checkedLike: 0,
                checkedDislike: 0,
            });
            app.reindex(app.vue.posts);
            app.reset_form();
            //app.init();
            app.goto('adding');
        });
    };
    
    app.reset_form = () => {
        app.vue.add_post_text = "";    
    };
    
    app.delete_post = (post_idx) => {
        let x = app.vue.posts[post_idx];
        axios.post(delete_post_url, {id: x.id}).then(() => {
            app.vue.posts.splice(post_idx, 1);
            app.reindex(app.vue.posts);
        });
    };
    
    app.goto = (destination) => {
        app.vue.page = destination;
        app.reset_form();
    };
    
    app.complete = (posts) => {
        posts.map((post) => {
            post.rating = 0;
            post.num_thumbs_display = 0;
            post.show_likers = 0;
            post.show_dislikers = 0;
            post.likers = "";
            post.dislikers = "";
            post.checkedLike = 0;
            post.checkedDislike = 0;
        });
    };
    
    app.set_thumbs = (post_idx, num_thumb) => {
        let post = app.vue.posts[post_idx];
        post.rating = num_thumb;
        axios.post(set_rating_url, {postID: post.id, rating: num_thumb});
    };
    app.thumbs_out = (post_idx) => {
        let post = app.vue.posts[post_idx];
        post.num_thumbs_display = post.rating;
    };
    app.thumbs_over = (post_idx, num_thumb) => {
        //let post = app.vue.posts[post_idx];
        //post.num_thumbs_display = num_thumb;
    };
    
    app.get_likers = (post_idx) => {
        let post = app.vue.posts[post_idx];
        post.show_likers = 1;
        axios.get(get_peopleLIKE_url, {params: {"postID": post.id}})
            .then((result) => {
                list = result.data.epicList;
                post.likers = list[0];
                //console.log(post.likers);
            }); 
    };

    app.get_dislikers = (post_idx) => {
        let post = app.vue.posts[post_idx];
        post.show_dislikers = 1;
        axios.get(get_peopleDISLIKE_url, {params: {"postID": post.id}})
            .then((result) => {
                list = result.data.epicList;
                post.dislikers = list[0];
                //console.log(post.dislikers);
            }); 
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        add_post: app.add_post,
        delete_post: app.delete_post,
        goto: app.goto,
        set_thumbs: app.set_thumbs,
        thumbs_out: app.thumbs_out,
        thumbs_over: app.thumbs_over,
        get_likers: app.get_likers,
        get_dislikers: app.get_dislikers,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_posts_url).then((result) => {
            //app.vue.posts = app.reindex(result.data.posts);
            //let posts = result.data.posts;
            let posts = result.data.posts;
            app.complete(posts);
            app.vue.posts = posts;
            
            app.vue.posts = app.reindex(result.data.posts);
            
            //I don't think the thing below is necessary.
            //app.vue.posts = response.data.posts;
        }).then(() => {
            for (let post of app.vue.posts) {
                axios.get(get_rating_url, {params: {"postID": post.id}})
                    .then((result) => {
                        post.rating = result.data.rating;
                        post.num_thumbs_display = result.data.rating;
                    });
            }
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);