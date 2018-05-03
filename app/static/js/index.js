(function () {
    const $totalPrice = document.querySelector('#total-price');

    // Estado de la aplicacion
    const state = {
        products: API.getProducts(),
        selectedProduct: null,
        quantity: 0,
        order: API.getOrder()
    }

    const refs = {}

    /**
     * Actualiza el valor del precio total
     **/
    function updateTotalPrice() {
        const totalPrice = state.selectedProduct.price * state.quantity;
        $totalPrice.innerHTML = `Precio total: $ ${totalPrice}`
    }

    /**
     * Dispara la actualizacion del precio total del producto
     * al cambiar el producto seleccionado
     **/
    function onProductSelect(selectedProduct) {
        state.selectedProduct = selectedProduct;
        updateTotalPrice();
    }

    /**
     * Dispara la actualizacion del precio total del producto
     * al cambiar la cantidad del producto
     **/
    function onChangeQunatity(quantity) {
        state.quantity = quantity;
        updateTotalPrice();
    }

    /**
     * Agrega un producto a una orden
     *
     **/
    function onAddProduct() {
        API.addProduct(1, state.selectedProduct, state.quantity)
            .then(function (r) {
                if (r.error) {
                    console.error(r.error);
                } else {
                    API.getOrder().then(function (data) {
                        refs.table.update(data);
                    });

                    refs.modal.close();
                }
            });
    }
    
    function onEdit(){
        API.editProduct(1, state.selectedProduct , state.quantity)
                    .then(function (r) {
                if (r.error) {
                    console.error(r.error);
                } else {
                    API.getOrder().then(function (data) {
                        refs.table.update(data);
                    });

                    refs.modal.close();
                }
            });
    }

    function edit(product) {
        const $quantity = document.querySelector('#quantity');
        const $select = document.querySelector('#select select');
    
       $quantity.value = product.quantity;
       $select.value = product.id;
    
       state.quantity = product.quantity;
       state.selectedProduct = product.id;
    
       // Abre el modal en forma de edición;
       refs.modal.open(edit);
    }
    
    window.edit = edit;    
    /**
     * Inicializa la aplicacion
     **/
    function init() {
        refs.modal = Modal.init({
            el: '#modal',
            products: state.products,
            onProductSelect: onProductSelect,
            onChangeQunatity: onChangeQunatity,
            onAddProduct: onAddProduct,
            onEdit: onEdit
        });

        // Inicializamos la tabla
        refs.table = Table.init({
            el: '#orders',
            data: state.order
        });
    }

    init();
    window.refs = refs;

})()

