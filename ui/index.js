$(document).ready(function () {
    var counter = 0;

    $("#addrow").on("click", function () {
        var newRow = $("<tr>");
        var cols = "";

        cols += '<td class="name"><input type="text" class="form-control" name="name' + counter + '"/></td>';
        cols += '<td class="mail"><input type="text" class="form-control" name="mail' + counter + '"/></td>';
        cols += '<td class="phone"><input type="text" class="form-control" name="phone' + counter + '"/></td>';


        cols += '<td><input type="button" class="ibtnSave btn btn-success "  value="Save"></td>';
        cols += '<td><input type="button" class="ibtnEdit btn btn-md btn-danger "  value="Edit"></td>';
        cols += '<td><input type="button" class="ibtnDel btn btn-md btn-danger "  value="Delete"></td>';
        newRow.append(cols);
        $("table.order-list").append(newRow);
        counter++;
    });



    $("table.order-list").on("click", ".ibtnDel", function (event) {
        $(this).closest("tr").remove();       
        counter -= 1
    });


    $("table.order-list").on("click", ".ibtnEdit", function (event) {
        $(this).closest("tr").remove();       
    });


    $("table.order-list").on("click", ".ibtnSave", function (event) {
        $(this).closest("tr").remove();       
        counter -= 1
    });



});


var monkeyList = new List('myTable', { 
  valueNames: ['name','mail','phone']
});




function calculateRow(row) {
    var price = +row.find('input[name^="price"]').val();

}

function calculateGrandTotal() {
    var grandTotal = 0;
    $("table.order-list").find('input[name^="price"]').each(function () {
        grandTotal += +$(this).val();
    });
    $("#grandtotal").text(grandTotal.toFixed(2));
}