module.exports = {
  setPayload: function(context, events, done) {
    context.vars.payload = {
      n: parseInt(context.vars.n, 10),
      times: parseInt(context.vars.times, 10)
    };
    return done();
  }
}
