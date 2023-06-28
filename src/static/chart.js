var chart = LightweightCharts.createChart(document.getElementById('chart'), {
	width: 1000,
  	height: 500,
	layout: {
		background: { type: 'solid', color: 'black' },
		textColor: '#ffffff',
	},
	grid: {
		vertLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
		horzLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
	},
	crosshair: {
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	priceScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
	timeScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
		timeVisible: true,
		secondsVisible: true,
	},
});

var candleSeries = chart.addCandlestickSeries({
	upColor: '#00ff00',
	downColor: '#ff0000', 
	borderDownColor: 'rgba(255, 144, 0, 1)',
	borderUpColor: 'rgba(255, 144, 0, 1)',
	wickDownColor: 'rgba(255, 144, 0, 1)',
	wickUpColor: 'rgba(255, 144, 0, 1)',
});


fetch('http://localhost:5000/history')
.then((r) => r.json())
.then((response) => {
	candleSeries.setData(response.map(item => {
		return {
			time: item.time / 1000,
			open: item.open,
			high: item.high,
			low: item.low,
			close: item.close
		}
	}));
})


var binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_5m");

binanceSocket.onmessage = function (event) {	
	var message = JSON.parse(event.data);

	var candlestick = message.k;

	candleSeries.update({
		time: candlestick.t / 1000,
		open: candlestick.o,
		high: candlestick.h,
		low: candlestick.l,
		close: candlestick.c
	})
}

var _predResults = null;
var addLineSeriespProccess = (_option, predResult) => {
	let _data = [];
	let _color = "";
	let _name;

	switch (_option) {
		case "lstm":
			_data = predResult.lstm;
			_color = "#0079FF";
			_name = "LSTM";
			break;
		case "rnn":
			_data = predResult.rnn;
			_color = "#F86F03";
			_name = "RNN";
			break;
		default:
			_data = predResult.xbg;
			_color = "#DD58D6";
			_name = "XGBoost";
	}

	const lineSeries = chart.addLineSeries({
		title: _name,
		color: _color,
		lineStyle: 0,
		lineWidth: 1,
		crosshairMarkerVisible: true,
		crosshairMarkerRadius: 6,
		lineType: 0,
	});

	lineSeries.setData(_data);
	chart.timeScale().fitContent();

	document.getElementById("loading").style.display = "none";
}

var getDataPrections = (_option) => {
	fetch('http://localhost:5000/predictions')
	.then((r) => r.json())
	.then((respone) => {
		_predResults = respone;
		addLineSeriespProccess(_option, _predResults);
	});
}

var predOptionProcess = (_option) => {
	document.getElementById("loading").style.display = "block";

	if (_predResults == null) {
		getDataPrections(_option);
	}
	else {
		addLineSeriespProccess(_option, _predResults);
	}
}