/*global WildRydes _config AmazonCognitoIdentity AWSCognito*/

var WildRydes = window.WildRydes || {};



(function rideScopeWrapper($) {
    var authToken;
    WildRydes.authToken
        .then(function setAuthToken(token) {
            if (token) {
                authToken = token;
            } else {
                window.location.href = "/signin.html";
            }
        })
        .catch(function handleTokenError(error) {
            // take user back to signin if token is not handled
            alert(error);
            window.location.href = "/signin.html";
        });

    var colnames = [
        "AccountName",
        "Balance",
        "Type",
        "PayoffDay",
        "PayoffSource",
        "CreditLimit"
    ];

    // variable for keeping track of groups of input radio buttons
    var inputRadioButtonGroupId=0;
    // variable for keywords indicating columns to skip
    var skipColKeywords = ["<p>","</p>","<span>","</span>","radio","<label>","</label>"];

    var actions = $("table td:last-child").html();

    // todo: share functions w/ budget
    function requestAccountInfo() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/budget-handling",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                RetrieveOrPlace: "retrieve",
                Entity: "account"
            }),
            contentType: "application/json",
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Error requesting ride: ",
                    textStatus,
                    ", Details: ",
                    errorThrown
                );
                console.error("Response: ", jqXHR.responseText);

                $("#modal-bank-input-error-help").modal("open");
                // alert(
                //     "An error occured when requesting your money trend:\n" +
                //         jqXHR.responseText
                // );
            }
        });
    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completeRequest(result) {
        console.log("Response received from API: ", result);
        var accountItems = result.BudgetItems
        for (idx in accountItems) {
            var accountRow = accountItems[idx];
            addNewRowFromRetrievedData(accountRow);
        }
        $(".sample").remove()

    }


    function placeAccountInfo() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/budget-handling",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                RetrieveOrPlace: "place",
                Entity: "account",
                AccountData: retrieveTableData()
            }),
            contentType: "application/json",
            success: completePostDataRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Error requesting ride: ",
                    textStatus,
                    ", Details: ",
                    errorThrown
                );
                console.error("Response: ", jqXHR.responseText);
                alert(
                    "An error occured while saving your bank balances:\n" +
                        jqXHR.responseText
                );
            }
        });
    }
    function retrieveTableData(event){

        //gets table
        var oTable = document.getElementById('account-table');//'table-bordered')[0];

        //gets rows of table
        var numRows = oTable.rows.length;

        var dictArray = [];

        //loops through rows (minus last ones with the button in it & start at 1 to not include the headers)
        for (i = 1; i < numRows - 2 ; i++){

          //gets cells of current row
           var oCells = oTable.rows.item(i).cells;

           //loops through each cell in current row
           // this should line up with colnames
           var dataObj = {};
           for(var j = 0; j < colnames.length; j++){
                  // get your cell info here
                  var colname = colnames[j];
                  var cellVal = oCells.item(j).innerHTML;
                  if(colnames[j]=="Type"){
                    var labelElements = oCells.item(j).getElementsByTagName("label");
                    Array.from(labelElements).forEach(labelElement =>{

                        // for(idx in labelElements)
                        // var labelElement = labelElements[idx];
                        var spanInnerText = labelElement.getElementsByTagName("span")[0].innerText;
                        var inputIsChecked = labelElement.getElementsByTagName("input")[0].checked;
                        if(inputIsChecked){
                            if(spanInnerText=="Checking"){
                                dataObj[colname] = "Checking";
                            } else if(spanInnerText=="Credit") {
                                dataObj[colname] = "Credit";
                            }
                        }


                    })
                  } else {
                    dataObj[colname] = cellVal;
                  }

               }
            dictArray.push(dataObj);
        }

        return dictArray

    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completePostDataRequest(result) {
        console.log('successfully posted account info data')

        M.toast({html: "Congrats, we received your Account Information",
                classes:"success-toast"});

        console.log("Response received from API: ", result);

    }


    function addNewRowFromRetrievedData(row) {
        var actions = $("table td:last-child").html();
        var index = $("table tbody tr:last-child").index();
        var rowHTML = "<tr>";
        for (idx in colnames) {
            var colname = colnames[idx];
            if(colname=="Type"){


                var creditChecked = (row[colname].includes("Credit")) ? "checked" : ""
                var checkingChecked = (row[colname].includes("Checking")) ? "checked" : ""

                inputRadioButtonGroupId += 1
                rowHTML += `<td><p>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" ${checkingChecked}/>
                                  <span>Checking</span>
                                </label>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" ${creditChecked}/>
                                  <span>Credit</span>
                                </label>
                              </p>
                            </td>`



            } else{
                rowHTML += `<td>${row[colname]}</td>`;
            }

        }

        rowHTML += `<td>${actions}</td>`;
        rowHTML += "</tr>";

        $("table").append(rowHTML);
        $("table tbody tr")
            .eq(index + 1)
            .find(".add, .edit");
        // $('[data-toggle="tooltip"]').tooltip();
    }


    $(document).ready(function() {
        var modal_elems = document.querySelectorAll('.modal')
        M.Modal.init(modal_elems,{})
        // $('[data-toggle="tooltip"]').tooltip();
        var actions = $("table td:last-child").html();
        var elems = document.querySelectorAll('.tooltipped');
        var instances = M.Tooltip.init(elems, {});

        requestAccountInfo();

        $('#submit-bank-info').click(placeAccountInfo);

        // Append table with add row form on add new button click
        $(".add-new").click(function() {
            $(this).attr("disabled", "disabled");
            var index = $("table tbody tr:last-child").index();
            var row_html = "<tr>";
            for (idx in colnames) {
                var colname = colnames[idx];


                if(colname=="Type"){

                inputRadioButtonGroupId += 1
                row_html += `<td><p>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio"/>
                                  <span>Checking</span>
                                </label>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" checked />
                                  <span>Credit</span>
                                </label>
                              </p>
                            </td>`
                } else {

                    row_html += `<td><input type="text" class="form-control" name="${colname}" id="${colname}"</td>`;
                }

            }

            row_html += `<td>${actions}</td>`;
            row_html += "</tr>";

            $("table").append(row_html);
            $("table tbody tr")
                .eq(index + 1)
                .find(".add, .edit")
                .toggle();
            //$('[data-toggle="tooltip"]').tooltip();
        });

        // Add row on add button click
        $(document).on("click", ".add", function() {
            var empty = false;
            var input = $(this)
                .parents("tr")
                .find('input[type="text"]');
            input.each(function() {
                if (!$(this).val()) {
                    $(this).addClass("error");
                    empty = true;
                } else {
                    $(this).removeClass("error");
                }
            });
            $(this)
                .parents("tr")
                .find(".error")
                .first()
                .focus();
            if (!empty) {
                input.each(function() {
                    $(this)
                        .parent("td")
                        .html($(this).val());
                });
                $(this)
                    .parents("tr")
                    .find(".add, .edit")
                    .toggle();
                $(".add-new").removeAttr("disabled");
            }
        });

        // Edit row on edit button click
        $(document).on("click", ".edit", function() {
            $(this)
                .parents("tr")
                .find("td:not(:last-child)")
                .each(function() {
                    // need some logic to skip dropdowns & radio buttons
                    var innerHTML = $(this).html();
                    var shouldSkip = skipColKeywords.every(el=>innerHTML.includes(el))
                    if(!shouldSkip){
                        $(this).html(
                            '<input type="text" class="form-control" value="' +
                                $(this).text() +
                                '">'
                        );

                    }
                });
            $(this)
                .parents("tr")
                .find(".add, .edit")
                .toggle();
            $(".add-new").attr("disabled", "disabled");
        });

        // Delete row on delete button click
        $(document).on("click", ".delete", function() {
            $(this)
                .parents("tr")
                .remove();
            $(".add-new").removeAttr("disabled");
        });
    });
})(jQuery);
