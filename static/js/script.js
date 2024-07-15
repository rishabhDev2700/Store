$(document).on('click', '.delete-button', function (e) {
    e.preventDefault();
    var item_id = $(this).data('index');
    $.ajax({
        type: 'POST',
        url: '{%url "orders:bag_delete"%}',
        data: {
            item: $(this).data('index'),
            csrfmiddlewaretoken: "{{csrf_token}}",
            action: 'post',
        },
        success: function (json) {
            $('.item[data-index="' + item_id + '"]').remove();
            if (json.quantity == 0) {
                subtotal = 0
            }
            else {
                subtotal = json.subtotal;
            }
            $('#subtotal').replaceWith = subtotal;
            $('#bag-quantity').replaceWith("json.quantity");
        }, error: function (xhr, errmsg, err) { },
    });
});

$(document).on("click", ".update-button", function (e) {
    e.preventDefault();
    var item_id = $(this).data("index");
    $.ajax({
        type: 'POST',
        url: '{%url "orders:bag_update"%}',
        data: {
            item: $(this).data("index"),
            quantity: $('#select' + item_id + " option:selected").text(),
            csrfmiddlewaretoken: "{{csrf_token}}",
            action: "post"
        },
        success: function (json) {
            subtotal = (parseFloat(json.subtotal)).toFixed(2);
            $("#bag-quantity").replaceWith(json.quantity);
            $("#subtotal").replaceWith(json.subtotal);
        },
        error: function (xhr, errmsg, err) { }
    });
});




$(document).ready(function () {
    $("#menu-button").on("click", function () {
        $("#menu").toggle("fast")
        $("#close").toggle("fast")
        $("nav").toggleClass("translate-x-full -translate-y-full")
    })
})