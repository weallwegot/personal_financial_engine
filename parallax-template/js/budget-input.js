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

    // shared values across function names
    const colnames = [
        "Description",
        "Amount",
        "Occurrence",
        "Type",
        "Sample_Date",
        "Source",
        "Until"
    ];

    // variable for keeping track of groups of input radio buttons
    var inputRadioButtonGroupId=0;
    // variable for keywords indicating columns to skip based on the html in the column
    const skipColKeywordsRadio = ["<p>","</p>",
    "<span>","</span>","radio",
    "<label>","</label>"];


    // materialize does some special stuff and makes divs like this
    const skipColKeywordsDropdown = ["select-dropdown","data-target","dropdown-trigger"];

    var accountNames = []

    function requestBudgetInfo() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/budget-handling",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                RetrieveOrPlace: "retrieve",
                Entity: "budget"
            }),
            contentType: "application/json",
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Error requesting budget: ",
                    textStatus,
                    ", Details: ",
                    errorThrown
                );
                console.error("Response: ", jqXHR.responseText);

                $("#modal-budget-input-error-help").modal("open");

            }
        });
    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completeRequest(result) {
        console.log("Response received from API: ", result);
        var budgetItemRows = result.BudgetItems;
        accountNames = result.AccountNames
        for (idx in budgetItemRows) {
            var row = budgetItemRows[idx];
            addNewRowFromRetrievedData(row);
        }
        $(".sample").remove()
    }


    function placeBudgetInfo() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/budget-handling",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                RetrieveOrPlace: "place",
                Entity: "budget",
                BudgetData: retrieveTableData()
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
                    "An error occured when posting your budget!:\n" +
                        jqXHR.responseText
                );
            }
        });
    }

    function retrieveTableData(event){

        //gets table
        var oTable = document.getElementById('budget-table');//'table-bordered')[0];

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
                  if(colname=="Type"){
                    var labelElements = oCells.item(j).getElementsByTagName("label");
                    // use Array.from to make html collection iterable
                    Array.from(labelElements).forEach(labelElement =>{

                        // for(idx in labelElements)
                        // var labelElement = labelElements[idx];
                        var spanInnerText = labelElement.getElementsByTagName("span")[0].innerText;
                        var inputIsChecked = labelElement.getElementsByTagName("input")[0].checked;
                        if(inputIsChecked){
                            if(spanInnerText=="In"){
                                dataObj[colname] = "Payment";
                            } else if(spanInnerText=="Out") {
                                dataObj[colname] = "Deduction";
                            }
                        }


                    })

                  } else if(colname=="Source") {
                    // create the dropdown but make it disabled when we read the data in and only enable on "edit" button press

                    var chosenAccount = oCells.item(j).getElementsByTagName("input")[0].value;
                    dataObj[colname] = chosenAccount;

                  }


                  else {
                    dataObj[colname] = cellVal;
                  }

               }
            dictArray.push(dataObj);
        }

        return dictArray

    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completePostDataRequest(result) {
        console.log('successfully posted budget info data')
        M.toast({html: "Congrats, we received your Budget Info",
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
                // check the appropriate radio button when new data is loaded from backend
                // todo: disable radio selection until the edit button is pressed
                var moneyInChecked = (row[colname].includes("Payment")) ? "checked" : ""
                var moneyOutChecked = (row[colname].includes("Deduction")) ? "checked" : ""

                inputRadioButtonGroupId += 1
                rowHTML += `<td><p>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" ${moneyInChecked}/>
                                  <span>In</span>
                                </label>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" ${moneyOutChecked}/>
                                  <span>Out</span>
                                </label>
                              </p>
                            </td>`


            } else if(colname=="Source"){
                // create dropdown input selection if column name is Source



                // accountNames.forEach((v) => {
                //                 var newOption = document.createElement("option");
                //                 newOption.value = v;
                //                 newOption.innerHTML = v;
                //                 sourceSelector.options.add(newOption);
                //             });

                var dropDownOptionsHTML = ``
                var accountSelector = document.createElement("select");
                for(idxAcctName in accountNames){
                    var currAcctName = accountNames[idxAcctName];
                    dropDownOptionsHTML += `<option value="${currAcctName}">${currAcctName}</option>`;

                    var newOption = document.createElement("option");
                    newOption.innerHTML = currAcctName;
                    newOption.value = currAcctName;
                    accountSelector.options.add(newOption)
                }

                accountSelector.disabled = false;



                rowHTML += `<td><div class="input-field">${accountSelector.outerHTML}</div></td>`;


            }

            else{
                rowHTML += `<td>${row[colname]}</td>`;
            }

        }

        rowHTML += `<td>${actions}</td>`;
        rowHTML += "</tr>";

        $("table").append(rowHTML);
        $("table tbody tr")
            .eq(index + 1)
            .find(".add, .edit");


        // initialize the dropdowns
        var elems = document.querySelectorAll("select");
        M.FormSelect.init(elems,{});
    }

    $(document).ready(function() {
        var modal_elems = document.querySelectorAll('.modal')
        M.Modal.init(modal_elems,{})
        var elems = document.querySelectorAll('.tooltipped');
        var instances = M.Tooltip.init(elems, {});
        // $('[data-toggle="tooltip"]').tooltip();
        var actions = $("table td:last-child").html();
        requestBudgetInfo();
        $('#place-budget-data').click(placeBudgetInfo);
        // Append table with add row form on add new button click
        $(".add-new").click(function() {
            $(this).attr("disabled", "disabled");
            var index = $("table tbody tr:last-child").index();
            var row_html = "<tr>";
            for (idx in colnames) {
                var colname = colnames[idx];


                if(colname=="Type"){
                    // create radio buttons for Type column

                    inputRadioButtonGroupId += 1
                    row_html += `<td><p>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio"/>
                                  <span>In</span>
                                </label>
                                <label>
                                  <input name="group${inputRadioButtonGroupId}" type="radio" checked />
                                  <span>Out</span>
                                </label>
                              </p>
                            </td>`
                } else if(colname=="Source") {
                    // create dropdown selection for Source column
                    var dropDownOptionsHTML = ``
                    var accountSelector = document.createElement("select");
                    for(idxAcctName in accountNames){
                        var currAcctName = accountNames[idxAcctName];
                        dropDownOptionsHTML += `<option value="${currAcctName}">${currAcctName}</option>`;

                        var newOption = document.createElement("option");
                        newOption.innerHTML = currAcctName;
                        newOption.value = currAcctName;
                        accountSelector.options.add(newOption)
                    }

                    accountSelector.disabled = false;



                    row_html += `<td><div class="input-field">${accountSelector.outerHTML}</div></td>`;


                }

                else {

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

            var elems = document.querySelectorAll("select");
            M.FormSelect.init(elems,{});
            // $('[data-toggle="tooltip"]').tooltip();
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
                    // todo: add logic to enable drop downs and radio buttons on "edit" button press
                    var innerHTML = $(this).html();
                    var isColumnRadio = skipColKeywordsRadio.every(el=>innerHTML.includes(el))
                    var isColumnDropdown = skipColKeywordsDropdown.every(el=>innerHTML.includes(el))
                    if(!isColumnDropdown && !isColumnRadio){
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
