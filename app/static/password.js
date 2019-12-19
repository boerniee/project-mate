function validatePassword(password) {
    if (password.length === 0) {
        document.getElementById("msg").innerHTML = "";
        return -1;
    }
    var matchedCase = new Array();
    matchedCase.push("[$@$§!%*#?&]");
    matchedCase.push("[A-Z]");
    matchedCase.push("[0-9]");
    matchedCase.push("[a-z]");

    var ctr = 0;
    for (var i = 0; i < matchedCase.length; i++) {
        if (new RegExp(matchedCase[i]).test(password)) {
            ctr++;
        }
    }
    if (password.length < 6) {
      return 0;
    }
    return ctr;
}
