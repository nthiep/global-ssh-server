$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2010 Q1',
            domain1: 2666,
            domain2: null,
            domain3: 2647
        }, {
            period: '2010 Q2',
            domain1: 2778,
            domain2: 2294,
            domain3: 2441
        }, {
            period: '2010 Q3',
            domain1: 4912,
            domain2: 1969,
            domain3: 2501
        }, {
            period: '2010 Q4',
            domain1: 3767,
            domain2: 3597,
            domain3: 5689
        }, {
            period: '2011 Q1',
            domain1: 6810,
            domain2: 1914,
            domain3: 2293
        }, {
            period: '2011 Q2',
            domain1: 5670,
            domain2: 4293,
            domain3: 1881
        }, {
            period: '2011 Q3',
            domain1: 4820,
            domain2: 3795,
            domain3: 1588
        }, {
            period: '2011 Q4',
            domain1: 15073,
            domain2: 5967,
            domain3: 5175
        }, {
            period: '2012 Q1',
            domain1: 10687,
            domain2: 4460,
            domain3: 2028
        }, {
            period: '2012 Q2',
            domain1: 8432,
            domain2: 5713,
            domain3: 1791
        }],
        xkey: 'period',
        ykeys: ['domain1', 'domain2', 'domain3'],
        labels: ['domain1', 'domain2', 'domain3'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "Domain 1",
            value: 5
        }, {
            label: "Domain 2",
            value: 10
        }, {
            label: "Domain 3",
            value: 8
        }],
        resize: true
    });

});
