<?php
return [

	/*
	*  System email address
	*  All messages will be from this address
	*/
	'system_email'  => $_ENV['SYSTEM_EMAIL'],
	'system_version' => 'Bahumut',

	/*
	*  Name of the sestem
	*  Messages sent out will use this name to refer to the system
	*/
	'name' => 'Materia',

	/*
	*  URLS throughout the system
	* \Uri::create('') will create full urls
	* If you're having issues with urls not being correct
	* You may wish to simply hard code these values
	*/
	'urls' => [
		'root'         => \Uri::create(''), // root directory http:://siteurl.com/
		'media'        => \Uri::create('media'), // where media is retrieved
		'media_upload' => \Uri::create('media/upload'), // where media is uploaded
		'play'         => \Uri::create('play/'), // game play  urls http://siteurl.com/play/3443
		'embed'        => \Uri::create('embed/'), // game embed urls http://siteurl.com/embed/3434
		'preview'      => \Uri::create('preview/'), // game preview urls http://siteurl.com/preview/3443
		'static'       => $_ENV['URLS_STATIC'] ?? \Uri::create(), // allows you to host another domain for static assets http://static.siteurl.com/
		'engines'      => $_ENV['URLS_ENGINES'] ?? \Uri::create('widget/'), // widget file locations
		// where are js and css assets hosted?
		// DEFAULT: public/dist (hosted as as https://site.com/)
		'js_css'       => \Uri::create('/'),
		// CDN PASS-THROUGH: set up aws cloudfront cdn have it load data from the default url
		//'js_css'     => '//xxxxxxxx.cloudfront.net/dist/',
		// CDN UNPKG.COM: load assets from npm module with the same release (version must match your version of materia)
		// 'js_css'    => '//unpkg.com/materia-server-client-assets@2.2.0/',
	],


	// Default media quota in bytes
	'media_quota' => 5000,

	'no_media_preview' => PUBPATH.'img/no-preview.jpg',

	'heroku_admin_warning' => $_ENV['IS_HEROKU'] ?? false,

	// amount of time before a draft auto-unlocks
	'lock_timeout' => 60 * 2,

	'debug_engines' => false,

	'send_emails' => $_ENV['BOOL_SEND_EMAILS'] ?? false,

	'default_api_version' => 2,

	// location of the lang files
	'lang_path' => [
		'login' => APPPATH.DS,
		'support' => APPPATH.DS
	],

	'default_users' => [
		// This user is used by the server to do management tasks, do not alter
		[
			'name'       => '~materia_system_only',
			'first_name' => 'Materia',
			'last_name'  => 'System',
			'email'      => 'materia_system@materia.ucf.edu',
			'roles'      => ['super_user','basic_author'],
			'password'   => $_ENV['USER_SYSTEM_PASSWORD'] ?? null,
		],
		[
			'name'       => '~author',
			'first_name' => 'Prof',
			'last_name'  => 'Author',
			'email'      => 'author@materia.ucf.edu',
			'roles'      => ['basic_author'],
			'password'   => $_ENV['USER_INSTRUCTOR_PASSWORD'] ?? null,
		],
		[
			'name'       => '~student',
			'first_name' => 'John',
			'last_name'  => 'Student',
			'email'      => 'student@materia.ucf.edu',
			'password'   => $_ENV['USER_STUDENT_PASSWORD'] ?? null,
		]
	],

	/**
	* Allow browser based widget uploads by administrators
	*/
	'enable_admin_uploader' => $_ENV['BOOL_ADMIN_UPLOADER_ENABLE'] ?? true,

	'google_tracking_id' => $_ENV['GOOGLE_ANALYTICS_ID'] ?? false,

	// Asset storage configuration
	'asset_storage_driver' => $_ENV['ASSET_STORAGE_DRIVER'] ?? 'file',

	'asset_storage' => [
		'file' => [
			'driver_class' => '\Materia\Widget_Asset_Storage_File',
			'media_dir'    => APPPATH.'media'.DS,
		],
		'db' => [
			'driver_class' => '\Materia\Widget_Asset_Storage_Db'
		],
		's3' => (
			(($_ENV['ASSET_STORAGE_DRIVER'] ?? 'file') == 's3')
			? [
				'driver_class' => '\Materia\Widget_Asset_Storage_S3',
				'credential_provider' => $_ENV['ASSET_STORAGE_S3_CREDENTIAL_PROVIDER'] ?? 'env',
				'endpoint'            => $_ENV['ASSET_STORAGE_S3_ENDPOINT'] ?? '', // set to url for testing endpoint (Not required for S3 on AWS)
				'region'              => $_ENV['ASSET_STORAGE_S3_REGION'] ?? 'us-east-1', // aws region for bucket
				'bucket'              => $_ENV['ASSET_STORAGE_S3_BUCKET'] ?? '', // bucket to store original user uploads
				'subdir'              => $_ENV['ASSET_STORAGE_S3_BASEPATH'] ?? 'media', // OPTIONAL - directory to store original and resized assets
				'secret_key'          => $_ENV['AWS_SECRET_ACCESS_KEY'] ?? $_ENV['ASSET_STORAGE_S3_SECRET'] ?? 'SECRET', // aws api secret key
				'key'                 => $_ENV['AWS_ACCESS_KEY_ID'] ?? $_ENV['ASSET_STORAGE_S3_KEY'] ?? 'KEY', // aws api key
				'token'               => $_ENV['AWS_SESSION_TOKEN'] ?? null,	// aws session token
				'fakes3_enabled'      => false, // using fakes3
			]
			: null
		),
	],

	'ai_generation' => [
		'enabled'      => filter_var($_ENV['GENERATION_ENABLED'] ?? false, FILTER_VALIDATE_BOOLEAN),
		'allow_images' => filter_var($_ENV['GENERATION_ALLOW_IMAGES'] ?? false, FILTER_VALIDATE_BOOLEAN),
		'provider'     => $_ENV['GENERATION_API_PROVIDER'] ?? '',
		'endpoint'     => $_ENV['GENERATION_API_ENDPOINT'] ?? '',
		'api_key'      => $_ENV['GENERATION_API_KEY'] ?? '',
		'api_version'  => $_ENV['GENERATION_API_VERSION'] ?? '',
		'model'        => $_ENV['GENERATION_API_MODEL'] ?? '',
		'log_stats'    => filter_var($_ENV['GENERATION_LOG_STATS'] ?? false, FILTER_VALIDATE_BOOLEAN)
	]

];
