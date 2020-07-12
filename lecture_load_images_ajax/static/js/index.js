// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        images: [], // List of objects, with an .name and .content.
        done: "",
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(callback_url).then((result) => {
            var image_promises = [];
            for (let img of result.data.images) {
                // We create an element in the images data structure.
                // Note: it is SUPER important here to have the url attribute
                // of img_el already defined.
                let img_el = {};
                app.vue.images.push(img_el);
                // We create a promise for when the image loads.
                let p = axios.get(
                    getimage_url,
                    {params: {"img": img}}).then((result) => {
                    // Puts the image URL.
                    // See https://vuejs.org/v2/guide/reactivity.html#For-Objects
                    Vue.set(img_el, 'url', result.data.imgbytes);
                    return "ok";
                });
                image_promises.push(p);
            }
            Promise.all(image_promises).then((r) => {
                    app.vue.done = "All done";
                    console.log(r);
            });
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
