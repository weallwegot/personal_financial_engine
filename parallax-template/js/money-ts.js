/*global WildRydes _config AmazonCognitoIdentity AWSCognito*/
var WildRydes = window.WildRydes || {};


(function rideScopeWrapper($) {
    var authToken;
    WildRydes.authToken.then(function setAuthToken(token) {
        if (token) {
            authToken = token;
        } else {
            window.location.href = '/signin.html';
        }
    }).catch(function handleTokenError(error) {
        // take user back to signin if token is not handled
        alert(error);
        window.location.href = '/signin.html';
    });

    function requestMoneyTimeseries() {
        $.ajax({
            method: 'POST',
            url: _config.api.invokeUrl + '/moneytimeseries',
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                Onward: {
                    TestPacket1: 12.04,
                    TestPacket2: 1906
                }
            }),
            contentType: 'application/json',
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error('Error requesting ride: ', textStatus, ', Details: ', errorThrown);
                console.error('Response: ', jqXHR.responseText);
                alert('An error occured when requesting your money trend:\n' + jqXHR.responseText);
            }
        });
    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completeRequest(result) {
        console.log('Response received from API: ',result)

        var dates = result.map(x=>x.date);
        var totals = result.map(x=>x.daily_total);

        var accounts = Object.keys(result[0]).filter(i=>(!i.endsWith("transactions") && i!="date" && i!="daily_total"))
        var account_balances = {};
        var idx;
        // for(idx in accounts){
        //     var acc = accounts[idx]
        //     if account_balances.hasOwnProperty(acc){
        //         account_balances[acc].push()
        //     } else {
        //         account_balances[acc] = []
        //     }
        // }




        var totals_trace = {
          x: dates,
          y: totals,
          type: 'scatter'
        };

        // var trace2 = {
        //   x: dates,
        //   y: ,
        //   type: 'scatter'
        // };

        var data = [totals_trace];

        Plotly.newPlot("money-ts-line-plot", data);
    }

    // Register click handler for #signout button
    $(function onDocReady() {

        $('#signOut').click(function() {
            WildRydes.signOut();
            alert("You have been signed out.");
            window.location = "signin.html";
        });
        requestMoneyTimeseries();

        WildRydes.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayUpdate('You are authenticated. Click to see your <a href="#authTokenModal" data-toggle="modal">auth token</a>.');
                $('.authToken').text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $('#noApiMessage').show();
        }
    });

    function displayUpdate(text) {
        $('#updates').append($('<li>' + text + '</li>'));
    }
}(jQuery));
