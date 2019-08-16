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

    function requestMoneyTimeseries() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/moneytimeseries",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                Onward: {
                    TestPacket1: 12.04,
                    TestPacket2: 1906
                }
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

                $("#modal-money-ts-error-help").modal("open")

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

        // get the forecasted data
        var forecastedMoneyResult = result.forecastData

        var dates = forecastedMoneyResult.map(x => x.date);
        var totals = forecastedMoneyResult.map(x => x.daily_total);

        var accounts = Object.keys(forecastedMoneyResult[0]).filter(
            i =>
                !i.endsWith("transactions") && i != "date" && i != "daily_total"
        );
        var account_balances = {};
        var idx;
        // calculate totals for each account name
        for (idx in accounts) {
            var accName = accounts[idx];
            var accDailyBalances = forecastedMoneyResult.map(x => x[accName]);
            var accDailyTxs = forecastedMoneyResult.map(x => x[accName + "transactions"]);
            account_balances[accName] = {
                x: dates,
                y: accDailyBalances,
                name: accName,
                text: accDailyTxs,
                type: "scatter"
            };
        }

        var totals_trace = {
            x: dates,
            y: totals,
            name: "Totals",
            type: "scatter"
        };

        var data = [totals_trace];
        // plot the forecsted data
        Plotly.newPlot(
            "money-ts-line-plot",
            data.concat(Object.values(account_balances))
        );

        // get the money warnings data
        var moneyWarnings = result.moneyWarningData;
        var warningsByAccount = {};
        var warningsCollapsible = $("#money-warning-list")[0];

        for(idx in accounts){


            var accName = accounts[idx];

            var iElement = document.createElement("i");
            iElement.classList.add("material-icons");
            iElement.innerText = "expand_more";


            var liElement = document.createElement("li");

            liElement.id = `${accName}-li`

            var divHeader = document.createElement("div");
            divHeader.classList.add("collapsible-header");
            divHeader.id = `${accName}-collapsible-header-div`;

            // divHeader.appendChild(iElement);
            divHeader.innerHTML = iElement.outerHTML;
            divHeader.innerHTML += `${accName} Warnings`;
            // put the collapsible div element in li
            liElement.appendChild(divHeader);
            // put the li element in the ul element
            warningsCollapsible.appendChild(liElement);
        }
        var idIter = 0;

        for(idx in moneyWarnings) {
            var warningObject = moneyWarnings[idx];
            var accName = warningObject.account;
            var accountDivElement = $(`#${accName}-collapsible-header-div`);

            var accountLiElement = $(`#${accName}-li`)[0];

            var divMoneyWarningContent = document.createElement("div");
            divMoneyWarningContent.id = `${accName}-content-warning-div-${idIter}`;
            divMoneyWarningContent.classList.add("collapsible-body");
            divMoneyWarningContent.innerHTML = `<span>${warningObject.date} - ${warningObject.issue} - ${warningObject.notes}. </br></span>`;

            accountLiElement.appendChild(divMoneyWarningContent)
            idIter += 1;

        }
        $('.collapsible').collapsible();

    }

    // Register click handler for #signout button
    $(function onDocReady() {
        $("#signOut").click(function() {
            WildRydes.signOut();
            alert("You have been signed out.");
            window.location = "signin.html";
        });


        var modal_elems = document.querySelectorAll('.modal')
        M.Modal.init(modal_elems,{})

        requestMoneyTimeseries();

        WildRydes.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayUpdate(
                    'You are authenticated. Click to see your <a href="#authTokenModal" data-toggle="modal">auth token</a>.'
                );
                $(".authToken").text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $("#noApiMessage").show();
        }
    });

    function displayUpdate(text) {
        $("#updates").append($("<li>" + text + "</li>"));
    }
})(jQuery);
