var tableRows = {{ json_table_rows }};

function populateTable()
{
    var regionTable = document.getElementById( "table_regions" );
    for ( var rowIndex in tableRows )
    {
        var currRow = tableRows[ rowIndex ];

        //console.log( "Found row: " + JSON.stringify( currRow ) );

        var regionTr = document.createElement("tr");

        // Provider
        var providerTd = document.createElement("td");
        var providerText = document.createTextNode( currRow['provider'] );
        providerTd.appendChild( providerText );
        regionTr.appendChild( providerTd );

        // Region Name
        var regionTd = document.createElement("td");
        var regionText = document.createTextNode( currRow[ 'region_name' ] );
        regionTd.appendChild( regionText );
        regionTr.appendChild( regionTd );

        // Geo Region
        var geoRegionTd = document.createElement("td");
        var geoRegionText = document.createTextNode( currRow[ 'geo_region' ] );
        geoRegionTd.appendChild( geoRegionText );
        regionTr.appendChild( geoRegionTd );

        // Countries
        var countriesTd = document.createElement("td");
        var countriesText = document.createTextNode( currRow[ 'display_countries' ].join( ', ') );
        countriesTd.appendChild( countriesText );
        regionTr.appendChild( countriesTd );

        // City
        var cityTd = document.createElement("td");
        var cityText = document.createTextNode( currRow[ 'city' ] );
        cityTd.appendChild( cityText );
        regionTr.appendChild( cityTd );

        regionTable.appendChild( regionTr );
    }

    // Now that data is in, display table to avoid so much jitter
    regionTable.style.display = "table";
}


function highlightSelectedProviders()
{
    var providers = [ "aws", "azure", "gcloud" ];
    for ( var i in providers )
    {
        var currProvider = providers[i];
        var currProviderTd = document.getElementById("cloud_" + currProvider);

        // Change their class to selected
        currProviderTd.classList.add( "provider_selected" );
    }


}


/**
 * Get the URL parameters
 * source: https://css-tricks.com/snippets/javascript/get-url-variables/
 * @param  {String} url The URL
 * @return {Object}     The URL parameters
 */
function getParams(url)
{ 
	var params = {};
	var parser = document.createElement('a');
	parser.href = url;
	var query = parser.search.substring(1);

    // If nothing in substring 1, return empty dict
    if ( query.length == 0 )
    {
        return {}
    }

    //console.log( "Query: \"" + query + "\"");
	var vars = query.split('&');
    //console.log( "vars: " + JSON.stringify(vars));

	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split('=');
		params[pair[0]] = decodeURIComponent(pair[1]);
	}

	return params;
}

function createState( urlParameters )
{
    // Prefix of window makes this a global
    window.applicationState = {
        "filters": {
            "providers"         : []
        },
        "sorting"  : {
            "field"             : null,
            "direction"         : null
        }
    };

    var allProviders = [ "aws", "azure", "gcloud" ];

    if ( Object.keys( urlParameters ).length == 0 )
    {
        console.log( "No keys in URL parameters!" );

        // Empty filter means all possible values are selected

        // Ascending sort on providers
        applicationState['sorting']['field']        = "cloud_provider";
        applicationState['sorting']['direction']    = 'asc';
    }
}


function updateUrlFromState()
{
    //format: "?filter_providers=[x,y,z]&sort_field=provider_name&sort_direction=asc"

    var baseUrl = getBaseUrl( window.location.href );

    console.log("Base URL: " + baseUrl );

    var parametersAddedToUrl = 0;

    var currUrl = baseUrl;

    // Check filters
    var filtersRef = window.applicationState["filters"];
    var filterKeys = Object.keys( filtersRef );
    for ( var i = 0; i < filterKeys.length; ++i )
    {
        var currFilterName = filterKeys[i];

        console.log("Curr filter: " + currFilter );

        var currFilter = window.applicationState["filters"][currFilterName];

        // If there are entries, add to URL 
        if ( currFilter.length > 0 )
        {
            console.log( "Need to update URL with filter " + currFilterName );
        }
    }

    // Add sorting info
    currUrl = addUrlParameter( currUrl, "sort_field", window.applicationState["sorting"]["field"] ); 
    currUrl = addUrlParameter( currUrl, "sort_direction", window.applicationState["sorting"]["direction"] );


    console.log( "Final URI after adding filters/sorting and URI encoding: " + currUrl );

    window.history.pushState( null, null, currUrl );
}

function addUrlParameter( startingUrl, newFieldName, newFieldValue )
{
    console.log( "adding parameter " + newFieldName + " to URL " + startingUrl );
    var startingParameters = getParams( startingUrl );

    var startingParameterCount = Object.keys( startingParameters ).length;

    console.log( "parameter count in starting URL: " + startingParameterCount );

    var updatedUrl = startingUrl;

    if ( startingParameterCount == 0 )
    {
        updatedUrl = updatedUrl + "?";
    }
    else 
    {
        updatedUrl = updatedUrl + "&";
    }

    updatedUrl = updatedUrl + newFieldName + "=";

    if ( Array.isArray(newFieldValue) == true ) 
    {
        updatedUrl = updatedUrl + JSON.stringify(newFieldValue);
    }
    else
    {
        updatedUrl = updatedUrl + newFieldValue;
    }

    return encodeURI(updatedUrl);
}


function getBaseUrl(url)
{
    // Find first question mark, return everything to left of it
    /*
    var pathArray = url.split( '/' );
    var protocol = pathArray[0];
    var host = pathArray[2].split('?')[0];
    var url = protocol + '//' + host + "/";
    */

    var startOfUrlParameters = url.indexOf( '?' );

    if ( startOfUrlParameters == -1 )
    {
        return url;
    }
    else 
    {
        return url.substr( 0, startOfUrlParameters );
    }
}


function main()
{
    var urlParams = getParams(window.location.href);

    console.log( "URL parameters: " + JSON.stringify(urlParams) );

    createState( urlParams );
    console.log( "Application state: " + JSON.stringify(window.applicationState) );

    updateUrlFromState();

    highlightSelectedProviders();

    populateTable();
}


main();
