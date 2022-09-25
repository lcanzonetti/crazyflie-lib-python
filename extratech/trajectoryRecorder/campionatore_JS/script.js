var c = document.getElementById("c");
var ctx = c.getContext("2d");
var cw = c.width = 800;
var ch = c.height = 400;
var cX = cw / 2,
  cY = ch / 2;
var rad = Math.PI / 180;

// size of the tangent
var t = 1 / 5;

// points array
var p = [{
  x: 100,
  y: 100
}, {
  x: 250,
  y: 150
}, {
  x: 300,
  y: 300
}, {
  x: 450,
  y: 250
}, {
  x: 510,
  y: 140
}, {
  x: 590,
  y: 250
}, {
  x: 670,
  y: 140
}];

function controlPoints(p) {
  // given the points array p calculate the control points
  var pc = [];
  for (var i = 1; i < p.length - 1; i++) {
    var dx = p[i - 1].x - p[i + 1].x; // difference x
    var dy = p[i - 1].y - p[i + 1].y; // difference y
    // the first control point
    var x1 = p[i].x - dx * t;
    var y1 = p[i].y - dy * t;
    var o1 = {
      x: x1,
      y: y1
    };

    // the second control point
    var x2 = p[i].x + dx * t;
    var y2 = p[i].y + dy * t;
    var o2 = {
      x: x2,
      y: y2
    };

    // building the control points array
    pc[i] = [];
    pc[i].push(o1);
    pc[i].push(o2);
  }
  return pc;
}

var pc = controlPoints(p); // the control points array

ctx.strokeStyle = "white";
ctx.fillStyle = "white";

function markers(p) {
  // markers dots & numbers
  for (var i = 0; i < p.length; i++) {
    ctx.beginPath();
    ctx.arc(p[i].x, p[i].y, 3, 0, 2 * Math.PI);
    ctx.font = "10pt Verdana";
    ctx.textAlign = "center";
    ctx.fillText(i, p[i].x, p[i].y - 15);
    ctx.stroke();
  }
}

function tangents(p) {
  var pc = controlPoints(p); // the control points array
  // tangents
  ctx.save();
  ctx.strokeStyle = "orange";
  for (var i = 1; i < pc.length; i++) {
    ctx.beginPath();
    ctx.moveTo(pc[i][0].x, pc[i][0].y);
    ctx.lineTo(pc[i][1].x, pc[i][1].y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawCurve(p) {

  var pc = controlPoints(p); // the control points array

  ctx.beginPath();
  ctx.moveTo(p[0].x, p[0].y);
  // the first & the last curve are quadratic Bezier
  // because I'm using push(), pc[i][1] comes before pc[i][0]
  ctx.quadraticCurveTo(pc[1][1].x, pc[1][1].y, p[1].x, p[1].y);

  if (p.length > 2) {
    // central curves are cubic Bezier
    for (var i = 1; i < p.length - 2; i++) {
      ctx.bezierCurveTo(pc[i][0].x, pc[i][0].y, pc[i + 1][1].x, pc[i + 1][1].y, p[i + 1].x, p[i + 1].y);
    }
    // the first & the last curve are quadratic Bezier
    var n = p.length - 1;
    ctx.quadraticCurveTo(pc[n - 1][0].x, pc[n - 1][0].y, p[n].x, p[n].y);
  }
  ctx.stroke();
}

drawCurve(p);
markers(p);
tangents(p);ripsc