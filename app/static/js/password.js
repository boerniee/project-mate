function validatePassword(password) {
    if (password.length === 0) {
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
    if (password.length < 8) {
      return 0;
    }
    return ctr;
}
